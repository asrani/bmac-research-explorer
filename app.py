from pathlib import Path
import math
import pandas as pd
import streamlit as st
from model import waiting_times, traversal

st.set_page_config(page_title='BMAC • Research Explorer', page_icon='🔄', layout='wide')
st.markdown('''<style>
.stApp {background: #f5f7fb;} [data-testid="stSidebar"] {background:#eaf0f7;}
h1,h2,h3 {letter-spacing:-.025em;} [data-testid="stMetric"] {background:white;padding:20px;border:1px solid #dce4ef;border-radius:14px;}
.block-container {padding-top:2.5rem;max-width:1400px;}
</style>''', unsafe_allow_html=True)
st.caption('WIRELESS NETWORKS-ON-CHIP  /  INTERACTIVE RESEARCH PROTOTYPE')
st.title('Explore bidirectional token access')
st.write('Compare ring traversal, inspect a simplified waiting-time model, and review the mesh-WiNoC results reported in the paper.')

with st.sidebar:
    st.header('Ring configuration')
    n=st.slider('Radio hubs',2,64,16)
    forwarding=st.number_input('Forwarding time · cycles',min_value=0.0,value=1.0,step=.5)
    holding=st.number_input('Holding time · cycles',min_value=0.0,value=8.0,step=1.0)
    occupancy=st.slider('Service occupancy ρ',0.0,1.0,.5,.05,help='Average fraction of hubs holding the token for transmission.')
    alpha=st.slider('Interpolation weight α',0.0,1.0,.5,.05,help='Illustrative weight between baseline and ideal service. Not a measured backtracking probability.')
    st.caption('Controls affect the analytical illustrations only. They do not change the reported experimental results.')
    pdf=Path(__file__).parent/'BMAC_revised.pdf'
    if pdf.exists(): st.download_button('Download paper · PDF',pdf.read_bytes(),'BMAC_revised.pdf','application/pdf',use_container_width=True)

r=waiting_times(n,forwarding,holding,occupancy,alpha)
cols=st.columns(3)
cols[0].metric('Baseline mean wait',f"{r['baseline']:.2f} cycles")
cols[1].metric('Ideal mean wait',f"{r['ideal']:.2f} cycles")
cols[2].metric('Illustrative mixture',f"{r['mixture']:.2f} cycles")
analysis,demo,results=st.tabs(['Waiting-time analysis','Token movement','Reported workloads'])
with analysis:
    st.subheader('How much can traversal direction change access delay?')
    st.info('The ideal policy chooses the shorter route using the request location. The paper’s local backtracking rule does not guarantee this behavior. The mixture is a heuristic, not a prediction of implemented BMAC latency.')
    distance=pd.DataFrame({'Token distance (hops)':range(n),
       'Unidirectional':[d*r['step'] for d in range(n)],
       'Ideal bidirectional':[min(d,n-d)*r['step'] for d in range(n)]})
    st.line_chart(distance,x='Token distance (hops)',y=['Unidirectional','Ideal bidirectional'],x_label='Forward distance from token to requester · hops',y_label='Token wait · cycles',color=['#64748b','#0d9488'])
    a,b=st.columns(2)
    with a:
        st.markdown('**Model assumptions**')
        st.write('One token, a logical ring, fixed average service-step time, and uniformly distributed request distance. Residual service time, queued competing requests, controller overhead, and fairness effects are omitted.')
        st.latex(r'T_s=T_f+\rho T_h,\qquad E[W_{base}]=\frac{N-1}{2}T_s')
        st.latex(r'E[W_{mix}]=\alpha E[W_{ideal}]+(1-\alpha)E[W_{base}]')
    with b:
        st.markdown('**Idealized worst-case comparison**')
        st.dataframe(pd.DataFrame({'Policy':['Unidirectional','Ideal shorter direction'],'Maximum wait (cycles)':[r['worst_baseline'],r['worst_ideal']]}),hide_index=True,use_container_width=True)
        st.caption('These bounds apply to the simplified service-step model, not to the local backtracking controller.')
    sizes=[]
    for size in range(2,65):
        rr=waiting_times(size,forwarding,holding,occupancy,alpha)
        sizes.append({'Hubs':size,'Baseline':rr['baseline'],'Ideal':rr['ideal'],'Mixture':rr['mixture']})
    st.markdown('**Sensitivity to ring size**')
    st.line_chart(pd.DataFrame(sizes),x='Hubs',y=['Baseline','Ideal','Mixture'],y_label='Mean token wait · cycles',color=['#64748b','#0d9488','#d97706'])
    st.download_button('Export distance analysis · CSV',distance.to_csv(index=False),'token_wait_analysis.csv','text/csv')
with demo:
    st.subheader('Follow a single request around the ring')
    st.caption('A deterministic traversal illustration. No packet queues or actual BMAC trigger logic are simulated. Hub IDs increase clockwise; ties use the forward direction.')
    c1,c2,c3=st.columns(3)
    start=c1.selectbox('Initial token hub',range(n),index=0)
    target=c2.selectbox('Requesting hub',range(n),index=n-1)
    policy=c3.selectbox('Traversal policy',['Unidirectional','Ideal shorter direction'])
    path=traversal(n,start,target,policy)
    # Include all configuration values so old frame state cannot exceed a new path length.
    if len(path)>1:
        frame=st.slider('Service step',0,len(path)-1,0,key=f'frame-{n}-{start}-{target}-{policy}')
    else:
        frame=0
        st.success('The requesting hub already holds the token; travel wait is zero in this model.')
    current=path[frame]
    points=[]
    for i in range(n):
        angle=2*math.pi*i/n-math.pi/2
        points.append((300+225*math.cos(angle),300+225*math.sin(angle)))
    svg=['<svg viewBox="0 0 600 600" role="img" aria-label="Token traversal ring" style="max-height:520px;width:100%">']
    for i,(x,y) in enumerate(points):
        xx,yy=points[(i+1)%n]
        svg.append(f'<line x1="{x}" y1="{y}" x2="{xx}" y2="{yy}" stroke="#cbd5e1" stroke-width="2"/>')
    for a,b in zip(path[:frame],path[1:frame+1]):
        x,y=points[a]; xx,yy=points[b]
        svg.append(f'<line x1="{x}" y1="{y}" x2="{xx}" y2="{yy}" stroke="#0d9488" stroke-width="5"/>')
    radius=16 if n<=32 else 10
    for i,(x,y) in enumerate(points):
        fill='#0d9488' if i==current else '#f59e0b' if i==target else '#ffffff'
        text='#ffffff' if i==current else '#0f172a'
        svg.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" stroke="#64748b"/><text x="{x}" y="{y+4}" text-anchor="middle" font-size="{11 if n<=32 else 8}" fill="{text}">{i}</text>')
    svg.append(f'<text x="300" y="285" text-anchor="middle" font-size="20" fill="#0f172a">Token at hub {current}</text><text x="300" y="315" text-anchor="middle" font-size="14" fill="#64748b">Step {frame} of {len(path)-1}</text></svg>')
    st.html(''.join(svg))
    st.caption('Teal: current token and traversed links · Amber: requesting hub · White: other hubs')
    st.write('Route: '+' → '.join(map(str,path)))
    st.write(f"Travel wait: **{(len(path)-1)*r['step']:.2f} cycles** at the selected average service-step time.")
with results:
    st.subheader('What the supplied paper reports')
    st.warning('Static source values, not fresh simulation outputs. The source reports slightly different rounded percentages and ratios; raw measurements are needed to reconcile them. Hotspot throughput is described as nearly unchanged without an exact numeric ratio here.')
    data=pd.DataFrame({'Workload':['Random','Shuffle','Transpose','Hotspot'],'Reported gain (%)':[61.,83.,36.,None],'Reported ratio':[1.62,1.84,None,None]})
    st.bar_chart(data.dropna(subset=['Reported gain (%)']),x='Workload',y='Reported gain (%)',color='#0d9488',y_label='Reported throughput increase · %')
    st.dataframe(data,hide_index=True,use_container_width=True)
    a,b=st.columns(2)
    a.metric('Hotspot latency · baseline','111 cycles')
    b.metric('Hotspot latency · BMAC','84 cycles',delta='−24.3%',delta_color='inverse')
    st.caption('Latency values are reported at the saturation PIR in the supplied paper. They are not derived from the sidebar controls.')
    with st.expander('Experimental setup and interpretation',expanded=True):
        st.write('64 cores (8 × 8 mesh), 16 radio hubs, 100,000 cycles including 1,000 warm-up cycles, 32-bit flits, XY routing, 1 GHz clock, and a 16 Gbps wireless link. The paper evaluates four synthetic workloads. It does not provide a validated energy or area model for this prototype.')
        st.write('The strongest reported throughput improvement occurs under shuffle traffic. Concentrated hotspot demand limits throughput gains. No claim of cycle-accurate simulation or new experimental validation is made by this app.')
    st.download_button('Export reported results · CSV',data.to_csv(index=False),'reported_workloads.csv','text/csv')
st.divider()
st.caption('BMAC Research Explorer • Prototype for explanation and discussion • Analytical estimates and source-reported experiments are kept separate.')
