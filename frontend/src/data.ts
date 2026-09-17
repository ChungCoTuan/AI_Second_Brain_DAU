// Lazy load data.json dynamically at runtime to avoid 1.5MB static JS bundle size.
export const DEMO_DATA: any = {
  soCanhBao: 26,
  soSuKien: 8,
  warnings: [],
  events: [],
  impact: [],
  docMeta: {},
  vbTuChet: [],
  vbSapChet: [],
  hanChot: [],
  chuaHieuLuc: [],
  diemMu: { mocTinhRa: 0 },
  suKienHieuLuc: [],
  nghiaVu: [],
  insights: { uuTien: [] },
  corpus: [],
  tongCorpus: 0,
  conSoChot: [],
  vbBo: [],
};

let dataLoaded = false;
const listeners: Array<() => void> = [];

export function onDataLoaded(cb: () => void) {
  if (dataLoaded) {
    cb();
  } else {
    listeners.push(cb);
  }
}

if (typeof window !== 'undefined') {
  fetch('/data.json')
    .then((res) => res.json())
    .then((data) => {
      Object.assign(DEMO_DATA, data);
      dataLoaded = true;
      listeners.forEach((fn) => fn());
      window.dispatchEvent(new CustomEvent('demo-data-loaded'));
    })
    .catch((err) => {
      console.warn('[DAU Second Brain] Could not load /data.json dynamically:', err);
    });
}
