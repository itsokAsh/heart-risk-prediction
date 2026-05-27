import Plot from 'react-plotly.js';

function GaugeChart({ riskScore }) {
  const score = Math.round(riskScore ?? 0);

  const data = [
    {
      type: 'indicator',
      mode: 'gauge+number',
      value: score,
      number: {
        suffix: '%',
        font: { size: 42, color: '#2b2a28', family: 'Source Sans 3, sans-serif' }
      },
      gauge: {
        axis: {
          range: [0, 100],
          tickwidth: 1,
          tickcolor: '#7d7a73',
          tickfont: { color: '#7d7a73', size: 11 },
          dtick: 20
        },
        bar: { color: 'rgba(74, 143, 138, 0.8)', thickness: 0.3 },
        bgcolor: 'rgba(255, 250, 244, 0.9)',
        borderwidth: 0,
        steps: [
          { range: [0, 20], color: 'rgba(92, 143, 116, 0.25)' },
          { range: [20, 40], color: 'rgba(197, 138, 87, 0.25)' },
          { range: [40, 100], color: 'rgba(178, 90, 87, 0.25)' }
        ],
        threshold: {
          line: { color: '#2b2a28', width: 3 },
          thickness: 0.8,
          value: score
        }
      }
    }
  ];

  const layout = {
    autosize: true,
    height: 280,
    margin: { t: 30, b: 10, l: 30, r: 30 },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: '#2b2a28', family: 'Source Sans 3, sans-serif' }
  };

  const config = {
    displayModeBar: false,
    responsive: true
  };

  return (
    <div className="gauge-container" id="gauge-chart">
      <Plot
        data={data}
        layout={layout}
        config={config}
        revision={score}
        useResizeHandler
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
}

export default GaugeChart;
