import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { useTheme } from '../theme/ThemeContext';
import styles from './HourlyHeatmap.module.css';

const DAYS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'];

const normalizeDay = (s) =>
  (s ?? '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');

export default function HourlyHeatmap({ data = [], loading }) {
  const svgRef = useRef(null);
  const wrapRef = useRef(null);
  const tipRef = useRef(null);
  const { theme } = useTheme();

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    if (!data.length) return;

    const byKey = new Map();
    data.forEach((d) => {
      const key = `${normalizeDay(d.nombre_dia)}|${d.hora_local}`;
      const cur = byKey.get(key) ?? 0;
      byKey.set(key, cur + (Number(d.total_escuchas) || 0));
    });
    const values = [...byKey.values()];
    const [min, max] = [d3.min(values) ?? 0, d3.max(values) ?? 1];

    const draw = (width) => {
      const cellH = 22;
      const margin = { top: 24, right: 12, bottom: 12, left: 76 };
      const w = Math.max(200, width - margin.left - margin.right);
      const h = 7 * cellH;
      svg.attr('width', width).attr('height', h + margin.top + margin.bottom);
      const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

      const x = d3.scaleBand().domain(d3.range(0, 24)).range([0, w]).padding(0.08);
      const y = d3.scaleBand().domain(DAYS).range([0, h]).padding(0.08);
      const color = d3.scaleLinear().domain([min, max]).range([theme.gradientD3[0], theme.gradientD3[2]]);

      g.append('g').call(d3.axisTop(x).tickValues(d3.range(0, 24, 3)));
      g.append('g').call(d3.axisLeft(y));

      const tip = d3.select(tipRef.current);
      DAYS.forEach((day) => {
        d3.range(0, 24).forEach((hour) => {
          const v = byKey.get(`${day}|${hour}`) ?? 0;
          g.append('rect')
            .attr('x', x(hour))
            .attr('y', y(day))
            .attr('width', x.bandwidth())
            .attr('height', y.bandwidth())
            .attr('rx', 3)
            .attr('fill', color(v))
            .on('mousemove', (e) => {
              d3.select(e.target).attr('stroke', theme.accentPrimary);
              tip.style('display', 'block').style('left', `${e.offsetX + 10}px`).style('top', `${e.offsetY}px`)
                .text(`${day} ${hour}h: ${v} escuchas`);
            })
            .on('mouseleave', (e) => {
              d3.select(e.target).attr('stroke', 'none');
              tip.style('display', 'none');
            });
        });
      });
    };

    const width = wrapRef.current?.clientWidth || 600;
    draw(width);
    const ro = new ResizeObserver((entries) => {
      const w = entries[0]?.contentRect.width;
      if (w) { svg.selectAll('*').remove(); draw(w); }
    });
    if (wrapRef.current) ro.observe(wrapRef.current);
    return () => { ro.disconnect(); svg.selectAll('*').remove(); };
  }, [data, theme]);

  return (
    <div className={styles.card}>
      <h2 className={styles.title}>Heatmap 24h x 7 días</h2>
      <div ref={wrapRef} className={styles.wrap}>
        {loading ? <span>Cargando…</span> : !data.length ? <span>Sin datos para filtros actuales.</span> : null}
        <svg ref={svgRef} role="img" aria-label="Heatmap horario" />
        <div ref={tipRef} className={styles.tooltip} />
      </div>
    </div>
  );
}
