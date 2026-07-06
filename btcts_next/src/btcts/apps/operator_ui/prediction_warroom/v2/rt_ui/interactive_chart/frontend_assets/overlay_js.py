# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/frontend_assets/overlay_js.py
# desc: Read-only overlay rendering JavaScript for WarRoom interactive chart.

from __future__ import annotations

CHART_OVERLAY_JS = r"""
function lineStyleValue(value) {
  if (value === 'dotted' && LightweightCharts.LineStyle) return LightweightCharts.LineStyle.Dotted;
  if (value === 'solid' && LightweightCharts.LineStyle) return LightweightCharts.LineStyle.Solid;
  if (LightweightCharts.LineStyle) return LightweightCharts.LineStyle.LargeDashed;
  return 2;
}
function renderLineOverlay(chart, layer) {
  if (!Array.isArray(layer.points) || layer.points.length < 2) return;
  let series = null;
  const options = { color: layer.color || '#7c3aed', lineWidth: layer.line_width || 2, lineStyle: lineStyleValue(layer.line_style || 'dashed'), priceLineVisible: false, lastValueVisible: false, title: layer.label || layer.layer_id || 'overlay' };
  if (chart.addSeries && LightweightCharts.LineSeries) {
    series = chart.addSeries(LightweightCharts.LineSeries, options);
  } else if (chart.addLineSeries) {
    series = chart.addLineSeries(options);
  }
  if (series) series.setData(layer.points.map(p => ({ time: p.time, value: p.value })));
}
function renderMarkerOverlay(baseSeries, layer) {
  if (!baseSeries || !Array.isArray(layer.markers) || !layer.markers.length) return;
  try {
    const markers = layer.markers.map(m => ({ time: m.time, position: m.position || 'aboveBar', color: m.color || layer.color || '#0f766e', shape: m.shape || 'circle', text: m.text || layer.label || '' }));
    if (LightweightCharts.createSeriesMarkers) LightweightCharts.createSeriesMarkers(baseSeries, markers);
    else if (baseSeries.setMarkers) baseSeries.setMarkers(markers);
  } catch (err) { console.debug(err); }
}
function renderBoardBandOverlay(chart, layer) {
  if (!Array.isArray(layer.points) || layer.points.length < 2) return;
  renderLineOverlay(chart, { layer_id: `${layer.layer_id || 'board_band'}_bid`, label: `${layer.label || 'board'} bid`, color: layer.bid_color || '#60a5fa', line_width: layer.line_width || 1, line_style: 'solid', points: layer.points.map(p => ({ time: p.time, value: p.bid })) });
  renderLineOverlay(chart, { layer_id: `${layer.layer_id || 'board_band'}_ask`, label: `${layer.label || 'board'} ask`, color: layer.ask_color || '#fb7185', line_width: layer.line_width || 1, line_style: 'solid', points: layer.points.map(p => ({ time: p.time, value: p.ask })) });
  renderLineOverlay(chart, { layer_id: `${layer.layer_id || 'board_band'}_mid`, label: `${layer.label || 'board'} mid`, color: layer.mid_color || '#64748b', line_width: layer.line_width || 1, line_style: 'dashed', points: layer.points.map(p => ({ time: p.time, value: p.mid })) });
}
function renderOverlayLayers(chart, baseSeries) {
  const layers = Array.isArray(BASE.overlay_layers) ? BASE.overlay_layers : [];
  for (const layer of layers) {
    if (!layer || layer.rendered_now === false) continue;
    if (layer.kind === 'line') renderLineOverlay(chart, layer);
    if (layer.kind === 'marker') renderMarkerOverlay(baseSeries, layer);
    if (layer.kind === 'board_band') renderBoardBandOverlay(chart, layer);
  }
}
function markSelection(series) {
  if (!selectedStart || !selectedEnd) return;
  const [s, e] = orderSelection(selectedStart, selectedEnd);
  const markers = [
    { time: s.time, position: 'belowBar', color: '#2563eb', shape: 'arrowUp', text: 'start' },
  ];
  if (Number(e.time) !== Number(s.time)) markers.push({ time: e.time, position: 'aboveBar', color: '#dc2626', shape: 'arrowDown', text: 'end' });
  try {
    if (LightweightCharts.createSeriesMarkers) {
      if (markersApi && markersApi.setMarkers) markersApi.setMarkers(markers); else markersApi = LightweightCharts.createSeriesMarkers(series, markers);
    }
  } catch (err) { console.debug(err); }
}
""".strip()
