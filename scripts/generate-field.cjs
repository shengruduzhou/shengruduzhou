const fs=require('node:fs');
const path=require('node:path');
function artwork(){
 const W=960,H=420,N=960,M=300,S=1,Y=88;
 const boxes=[[-2.9,0,3.6,-1.9,3.25,4.5,0],[1.9,0,3.6,2.9,3.25,4.5,0],[-2.9,2.75,3.6,2.9,3.25,4.5,0],[-.9,0,5.55,.9,1.8,7.15,1],[-5.2,0,-1.4,-4.65,3.6,1.4,0],[4.3,0,-1.8,5.3,2.4,-.8,0],[4.3,0,.8,5.3,2.4,1.8,0],[4.3,2.1,-1.8,5.3,2.4,1.8,0],[-1.3,0,-5.1,1.3,.36,-3.7,0],[-3.5,0,7.6,-2.9,3.65,8.15,0],[2.9,0,7.6,3.5,3.65,8.15,0],[-3.5,3.15,7.6,3.5,3.65,8.15,0]];
 const O=[0,1.45,0],TAU=2*Math.PI;
 const pal=Array.from({length:32},(_,i)=>{const q=i/31;return '#'+[17+q*220,20+q*216,17+q*206].map(v=>Math.round(v).toString(16).padStart(2,'0')).join('')});
 const lime=['#37461d','#536829','#78983e','#a6ce50','#c9f36b','#e2faa9'];
 function hit(d){let best=1e9,n=[0,0,0],mat=0,xyz=[];function take(t,nn,mm){if(t>1e-5&&t<best){best=t;n=nn;mat=mm;xyz=O.map((v,i)=>v+t*d[i]);}};
  for(let a=0;a<3;a++){if(Math.abs(d[a])<1e-8)continue;const bound=a===1?[0,4.1]:a===0?[-9,9]:[-10,10];const v=d[a]>0?bound[1]:bound[0];let nn=[0,0,0];nn[a]=-Math.sign(d[a]);take((v-O[a])/d[a],nn,a===1?(d[a]<0?2:3):4);}
  for(const b of boxes){let lo=-1e9,hi=1e9,axis=0,sgn=0;for(let a=0;a<3;a++){if(Math.abs(d[a])<1e-8){if(O[a]<b[a]||O[a]>b[a+3]){lo=1e9;hi=-1e9;break;}continue;}let t0=(b[a]-O[a])/d[a],t1=(b[a+3]-O[a])/d[a];let near=Math.min(t0,t1);if(near>lo){lo=near;axis=a;sgn=-Math.sign(d[a]);}hi=Math.min(hi,Math.max(t0,t1));}if(lo<=hi&&lo>0){let nn=[0,0,0];nn[axis]=sgn;take(lo,nn,b[6]);}}
  const [x,y,z]=xyz;
  function light(px,py,pz,power){let v=[px-x,py-y,pz-z];let dist=Math.hypot(...v);v=v.map(q=>q/dist);const nd=Math.max(0,v.reduce((sum,q,i)=>sum+q*n[i],0));if(nd<=0)return 0;let o=xyz.map((q,i)=>q+1e-4*n[i]);for(const b of boxes){let lo=0,hi=dist-1e-4;for(let i=0;i<3;i++){if(Math.abs(v[i])<1e-8){if(o[i]<b[i]||o[i]>b[i+3]){lo=1;hi=0;break;}continue;}let a=(b[i]-o[i])/v[i],z=(b[i+3]-o[i])/v[i];lo=Math.max(lo,Math.min(a,z));hi=Math.min(hi,Math.max(a,z));}if(lo<=hi&&hi>0)return 0;}return power*nd/(1+.11*dist*dist);}
  let diffuse=light(-2.4,3.95,1.5,1.10)+light(4.6,3.95,-3.6,.9)+light(0,3.85,8.8,1.15);
  let l=.13+.54*Math.max(0,n[1])+.44*Math.max(0,-n[2])+.27*Math.max(0,n[0]);l*=.62+.38*Math.exp(-best/10);if(mat===1)return lime[Math.min(5,Math.floor((.36+l)*7))];
  if(mat===2){const edge=Math.min(Math.abs(x-Math.round(x)),Math.abs(z-Math.round(z)));l=.08+.12*Math.exp(-best/8)+diffuse*.67;if(edge<.014+best*.0018)l+=.16;const shadow=boxes.some(b=>x>b[0]-.17&&x<b[3]+.17&&z>b[2]-.45&&z<b[5]+.45);if(shadow)l*=.55;}
  if(mat===3){l=.08+.13*Math.exp(-best/12);if(Math.abs(x)<.17&&Math.abs(z)<8)l=.96;else if(Math.abs(z-Math.round(z/2)*2)<.018)l+=.10;}
  if(mat===4){l=.07+.10*Math.exp(-best/12)+(n[2]!==0?.05:0)+diffuse*.85;const edge=Math.min(Math.abs((n[0]!==0?z:x)-Math.round((n[0]!==0?z:x)/2)*2),Math.abs(y-Math.round(y/2)*2));if(edge<.028)l-=.07;}
  if(mat===0){l=l*.50+.08+diffuse*.9;const face=n.findIndex(v=>v!==0);let uv=xyz.filter((_,i)=>i!==face);if(uv.some(v=>Math.abs(v-Math.round(v))<.011))l-=.06;}
  return pal[Math.max(0,Math.min(pal.length-1,Math.round(l*(pal.length-1))))];
 }
 let groups={};for(let j=0;j<M;j++){let lat=(.5-(j+.5)/M)*Math.PI*.625;let row=[];for(let i=0;i<N;i++){let lon=((i+.5)/N-.5)*TAU;row.push(hit([Math.cos(lat)*Math.sin(lon),Math.sin(lat),Math.cos(lat)*Math.cos(lon)]));}for(let a=0;a<N;){let b=a+1;while(b<N&&row[b]===row[a])b++;(groups[row[a]]??=[]).push(`M${a*S} ${Y+j*S}h${(b-a)*S}v${S}h-${(b-a)*S}z`);a=b;}}
 const paths=Object.entries(groups).map(([c,d])=>`<path fill="${c}" d="${d.join('')}"/>`).join('');
 const marks=Array.from({length:13},(_,i)=>`<path d="M${i*80} 388v${i%3===0?9:5}"/>`).join('');
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-labelledby="title desc"><title id="title">Field 001 — a procedural panoramic space</title><desc id="desc">An illustrative computer-generated interior, ray-cast across a full 360 degrees of longitude and a cropped vertical field. A lime cuboid marks the forward direction. The vertical field spans 112.5 degrees.</desc><rect width="960" height="420" fill="#141714"/>${paths}<path d="M0 238H960" fill="none" stroke="#e4e5da" stroke-opacity=".17" stroke-dasharray="3 6"/><path d="M480 88V388" stroke="#c9f36b" stroke-opacity=".55" stroke-dasharray="3 6"/><g fill="none" stroke="#c9f36b" stroke-width="1.6"><path d="M447 209v-11h11M513 209v-11h-11M447 281v11h11M513 281v11h-11"/></g><g font-family="monospace" font-size="13" fill="#e4e5da"><text x="20" y="23" letter-spacing="1" fill="#c9f36b">FIELD 001</text><text x="20" y="66" font-family="Arial, Helvetica, sans-serif" font-weight="bold" font-size="39" letter-spacing="-1.4">Panoramic vision</text><text x="940" y="30" text-anchor="end">SYNTHETIC SCENE</text><text x="940" y="64" font-family="Arial, Helvetica, sans-serif" font-weight="bold" font-size="29" text-anchor="end" fill="#c9f36b">360°</text><text x="14" y="412">-180</text><text x="240" y="412" text-anchor="middle">-90</text><text x="480" y="412" text-anchor="middle" fill="#c9f36b">0</text><text x="720" y="412" text-anchor="middle">90</text><text x="946" y="412" text-anchor="end">180</text></g><g fill="none" stroke="#979c91" stroke-width="1">${marks}</g></svg>`;
}
if(require.main===module){const out=process.argv[2]||path.join(__dirname,'../assets/field');fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'field-001.svg'),artwork());}
module.exports=artwork;
