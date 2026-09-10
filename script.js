const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>[...r.querySelectorAll(s)];
let meetups=[],activeRegion='all',query='',mapInstance=null;

function ordinalWeekdayDate(schedule){
  const now=new Date(),y=now.getFullYear(),m=now.getMonth();
  const weekdays={sunday:0,monday:1,tuesday:2,wednesday:3,thursday:4,friday:5,saturday:6};
  const ord={first:1,second:2,third:3,fourth:4};
  const clean=schedule.toLowerCase();
  const match=clean.match(/(first|second|third|fourth)\s+(sunday|monday|tuesday|wednesday|thursday|friday|saturday)/);
  const last=clean.match(/last\s+(sunday|monday|tuesday|wednesday|thursday|friday|saturday)/);
  function calc(year,month){
    if(match){
      const target=weekdays[match[2]],n=ord[match[1]],first=new Date(year,month,1),offset=(target-first.getDay()+7)%7;
      return new Date(year,month,1+offset+7*(n-1));
    }
    if(last){
      const target=weekdays[last[1]],d=new Date(year,month+1,0),offset=(d.getDay()-target+7)%7;
      return new Date(year,month,d.getDate()-offset);
    }
    const dayMatch=clean.match(/(?:^|\s)(\d{1,2})(?:st|nd|rd|th)\s+of\s+month/);
    if(dayMatch)return new Date(year,month,Number(dayMatch[1]));
    return null;
  }
  let d=calc(y,m);
  if(d&&d<new Date(now.getFullYear(),now.getMonth(),now.getDate()))d=calc(y,m+1);
  return d;
}

function formatDate(d){
  return new Intl.DateTimeFormat('en-GB',{weekday:'short',day:'numeric',month:'short'}).format(d);
}

function escapeHtml(v=''){
  return String(v).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
}
function escapeAttr(v=''){return escapeHtml(v);}

function extract(){
  fetch('meetups-source.html',{cache:'no-store'})
    .then(r=>{if(!r.ok)throw new Error('Meetup source unavailable');return r.text();})
    .then(html=>{
      const doc=new DOMParser().parseFromString(html,'text/html');
      meetups=[];
      $$('.region-section',doc).forEach(section=>{
        const region=$('.region-header',section)?.textContent.trim()||'Other';
        $$('.meetup-item',section).forEach(item=>{
          const nameNode=$('.meetup-name',item);
          if(!nameNode)return;
          const clone=nameNode.cloneNode(true);
          $$('.status-tag',clone).forEach(n=>n.remove());
          const name=clone.textContent.trim();
          const status=$('.status-tag',item)?.textContent.trim()||'Active';
          const schedule=$('.meetup-schedule',item)?.textContent.trim()||'';
          const links=$$('.meetup-links a',item).map(a=>({label:a.textContent.trim(),href:a.getAttribute('href')}));
          const linkText=$('.meetup-links',item)?.textContent.trim()||'';
          const lat=Number.parseFloat(item.dataset.lat);
          const lon=Number.parseFloat(item.dataset.lon);
          meetups.push({name,region,status,schedule,links,linkText,lat,lon});
        });
      });
      const activeCount=meetups.filter(m=>m.status.trim().toLowerCase()==='active').length;
      $('#hero-count').textContent=activeCount;
      render();
      renderMap();
    })
    .catch(()=>{
      $('#hero-count').textContent='—';
      $('#results-count').textContent='Could not load meetup listings.';
      const map=$('#meetup-map');
      if(map)map.innerHTML='<p class="map-error">Could not load meetup locations.</p>';
    });
}

function card(m){
  const paused=m.status.toLowerCase().includes('paused');
  const next=paused?null:ordinalWeekdayDate(m.schedule);
  const links=m.links.length
    ?m.links.map(l=>`<a href="${escapeAttr(l.href)}" target="_blank" rel="noopener">${escapeHtml(l.label)}</a>`).join('')
    :(m.linkText?`<span class="region-tag">${escapeHtml(m.linkText)}</span>`:'');
  return `<article class="meetup-card"><div class="card-top"><h3>${escapeHtml(m.name)}</h3><span class="region-tag">${escapeHtml(m.region)}</span></div><div class="status ${paused?'paused':''}">${escapeHtml(m.status)}</div><p class="schedule">${escapeHtml(m.schedule)}</p>${next?`<p class="next-date">Next expected: <strong>${formatDate(next)}</strong></p>`:''}<div class="card-links">${links}</div></article>`;
}

function render(){
  const q=query.trim().toLowerCase();
  const visible=meetups.filter(m=>(activeRegion==='all'||m.region===activeRegion)&&(!q||`${m.name} ${m.region} ${m.schedule} ${m.linkText}`.toLowerCase().includes(q)));
  $('#meetup-grid').innerHTML=visible.map(card).join('');
  $('#results-count').textContent=`${visible.length} meetup${visible.length===1?'':'s'} shown`;
  $('#empty-state').hidden=visible.length!==0;
  $('#clear-search').hidden=!q&&activeRegion==='all';
}

function mapPopup(m){
  const paused=m.status.toLowerCase().includes('paused');
  const links=m.links.length
    ?`<div class="map-popup-links">${m.links.map(l=>`<a href="${escapeAttr(l.href)}" target="_blank" rel="noopener">${escapeHtml(l.label)}</a>`).join('')}</div>`
    :(m.linkText?`<div class="map-popup-note">${escapeHtml(m.linkText)}</div>`:'');
  return `<div class="map-popup"><strong>${escapeHtml(m.name)}</strong><span class="map-popup-status ${paused?'paused':''}">${escapeHtml(m.status)}</span><p>${escapeHtml(m.schedule)}</p>${links}</div>`;
}

function renderMap(){
  const el=$('#meetup-map');
  if(!el||typeof L==='undefined')return;
  if(mapInstance){mapInstance.remove();mapInstance=null;}

  const mapped=meetups.filter(m=>Number.isFinite(m.lat)&&Number.isFinite(m.lon));
  if(!mapped.length){el.innerHTML='<p class="map-error">No meetup locations are available.</p>';return;}

  mapInstance=L.map(el,{scrollWheelZoom:false,preferCanvas:true,zoomControl:true});
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    maxZoom:19,
    attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(mapInstance);

  const bounds=[];
  mapped.forEach(m=>{
    const paused=m.status.toLowerCase().includes('paused');
    const marker=L.circleMarker([m.lat,m.lon],{
      radius:paused?6:7,
      color:paused?'#737373':'#c66f00',
      weight:2,
      fillColor:paused?'#8a8a8a':'#f7931a',
      fillOpacity:0.92
    }).addTo(mapInstance);
    marker.bindPopup(mapPopup(m),{maxWidth:300});
    bounds.push([m.lat,m.lon]);
  });

  mapInstance.fitBounds(bounds,{padding:[28,28],maxZoom:7});

  const legend=L.control({position:'bottomright'});
  legend.onAdd=()=>{
    const div=L.DomUtil.create('div','map-legend');
    div.innerHTML='<span><i class="legend-dot active"></i>Active</span><span><i class="legend-dot paused"></i>Paused</span>';
    return div;
  };
  legend.addTo(mapInstance);
}

document.addEventListener('DOMContentLoaded',()=>{
  extract();
  const menu=$('.menu-toggle'),nav=$('#site-nav');
  menu?.addEventListener('click',()=>{const open=nav.classList.toggle('open');menu.setAttribute('aria-expanded',String(open));});
  $$('#site-nav a').forEach(a=>a.addEventListener('click',()=>{nav.classList.remove('open');menu?.setAttribute('aria-expanded','false');}));
  $('#directory-search')?.addEventListener('input',e=>{query=e.target.value;$('#hero-search').value=e.target.value;render();});
  $('#hero-search-form')?.addEventListener('submit',e=>{e.preventDefault();query=$('#hero-search').value;$('#directory-search').value=query;activeRegion='all';$$('.filter').forEach(b=>b.classList.toggle('active',b.dataset.region==='all'));render();$('#meetups').scrollIntoView({behavior:'smooth'});});
  $$('.filter').forEach(btn=>btn.addEventListener('click',()=>{activeRegion=btn.dataset.region;$$('.filter').forEach(b=>b.classList.toggle('active',b===btn));render();}));
  $('#clear-search')?.addEventListener('click',()=>{query='';activeRegion='all';$('#directory-search').value='';$('#hero-search').value='';$$('.filter').forEach(b=>b.classList.toggle('active',b.dataset.region==='all'));render();});
});
