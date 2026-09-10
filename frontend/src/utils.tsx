import React from 'react';

export function esc(s: any): string {
  if (s == null) return '';
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

export function fmtDate(s: any): string {
  if (!s) return '';
  const p = String(s).split('-');
  return p.length === 3 ? `${p[2]}/${p[1]}/${p[0]}` : String(s);
}

export function fold(s: any): string {
  return String(s == null ? '' : s)
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D')
    .toLowerCase();
}

export function hl(goc: any, q: string): React.ReactNode {
  const s = String(goc == null ? '' : goc);
  if (!q) return s;
  
  const map: number[] = [];
  let f = "";
  for (let i = 0; i < s.length; i++) {
    const c = s[i]
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/đ/g, "d")
      .replace(/Đ/g, "D")
      .toLowerCase();
    for (let k = 0; k < c.length; k++) map.push(i);
    f += c;
  }
  
  const at = f.indexOf(q);
  if (at < 0) return s;
  
  const a = map[at];
  const b = at + q.length < map.length ? map[at + q.length] : s.length;
  
  return (
    <>
      {s.slice(0, a)}
      <mark style={{ background: '#fde68a', color: 'inherit', padding: '0 2px', borderRadius: '3px' }}>
        {s.slice(a, b)}
      </mark>
      {s.slice(b)}
    </>
  );
}

export function nhanNgay(ngay: string): string {
  if (!ngay) return '';
  if (ngay.startsWith('--')) {
    const p = ngay.split('-');
    return `hằng năm, ngày ${p[3]}/${p[2]}`;
  }
  return fmtDate(ngay);
}

export const HOM_NAY = '2026-08-19';

export function ngayTu(a: string, b: string): number {
  return Math.round((Date.parse(b + 'T00:00:00Z') - Date.parse(a + 'T00:00:00Z')) / 86400000);
}

export function mucDo(ngay: string): 'lap' | 'qua' | 'gan' | 'sau' {
  if (!ngay || ngay.startsWith('--')) return 'lap';
  const d = ngayTu(HOM_NAY, ngay);
  return d < 0 ? 'qua' : d <= 120 ? 'gan' : 'sau';
}

export function conLai(ngay: string): string {
  if (!ngay || ngay.startsWith('--')) return '<span class="dleft">lặp hằng năm</span>';
  const d = ngayTu(HOM_NAY, ngay);
  const c = mucDo(ngay);
  const text = d < 0 ? `quá ${-d} ngày` : d === 0 ? 'hôm nay' : `còn ${d} ngày`;
  return `<span class="dleft ${c}">${text}</span>`; // This one is still returning HTML string! Wait.
}

export function conLaiNode(ngay: string): React.ReactNode {
  if (!ngay || ngay.startsWith('--')) return <span className="dleft">lặp hằng năm</span>;
  const d = ngayTu(HOM_NAY, ngay);
  const c = mucDo(ngay);
  const text = d < 0 ? `quá ${-d} ngày` : d === 0 ? 'hôm nay' : `còn ${d} ngày`;
  return <span className={`dleft ${c}`}>{text}</span>;
}

export function badge(lyDo: string): string {
  return lyDo.includes('bãi bỏ') ? 'repeal' : 'replace';
}
