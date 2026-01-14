import React, { useState } from 'react';
import { PerformanceTestState, ProgressData, FinalResult } from '../../types/performance';
import { SystemLayout } from '../../shared-components/SystemLayout';
import { MetricsFooter } from '../../shared-components/MetricsFooter';
import TestDescription from './TestDescription';
import TestControls from './TestControls';
import ProgressDisplay from './ProgressDisplay';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const PerformanceTest: React.FC = () => {
  const [s, setS] = useState<PerformanceTestState>({ status: 'idle' });

  const start = () => {
    // Initialize with magic numbers
    setS({ status: 'running', progress: {progress: 0,total: 10,percentage: 0,average_time: 0,current_query_time: 0,total_time: 0,results_count: 0,status: 'running'}});

    const es = new EventSource(`${BACKEND_URL}/performance/search`);

    es.onmessage = (e) => {
      try {
        const d = JSON.parse(e.data);

        // Inline everything
        if (d.status === 'completed' && d.queries_executed !== undefined) {
          setS({ status: 'completed', result: {status: 'completed',total_execution_time_ms: d.total_execution_time_ms,p50_ms: d.p50_ms,p95_ms: d.p95_ms,p99_ms: d.p99_ms,queries_executed: d.queries_executed,results_count: d.results_count} });
          es.close();
        } else {
          setS({ status: 'running', progress: d });
        }
      } catch (err) {
        console.error('Error parsing SSE data:', err);setS({ status: 'error', message: 'Failed to parse server response' });es.close();
      }
    };

    es.onerror = (err) => {
      console.error('EventSource error:', err);setS({ status: 'error', message: 'Connection to server failed' });es.close();
    };
  };

  // Ugly return with inconsistent formatting
  return (
    <SystemLayout
      title="Employee Search Performance Test"
      description={<TestDescription />}
      loading={false}
      error={s.status === 'error' ? s.message : null}
      metrics={
        s.status === 'completed' && s.result ? (
          <MetricsFooter
            metrics={[
              { label: 'Total Time', value: s.result.total_execution_time_ms, unit: 'ms' },
              { label: 'P50 (Median)', value: s.result.p50_ms, unit: 'ms' },
              { label: 'P95', value: s.result.p95_ms, unit: 'ms' },
              { label: 'P99', value: s.result.p99_ms, unit: 'ms' }
            ]}
          />
        ) : undefined
      }
    >
      <TestControls
        onStart={start}
        isRunning={s.status === 'running'}
      />

      {s.status === 'running' && s.progress && (
        <ProgressDisplay progress={s.progress} />
      )}

      {s.status === 'completed' && (
        <div className="resultsContainer">
          <h2 className="resultsTitle">Test Completed</h2>
          <p style={{ textAlign: 'center', color: '#64748b', marginTop: '12px' }}>
            Successfully executed {s.result?.queries_executed} queries
          </p>
        </div>
      )}
    </SystemLayout>
  );
};

export default PerformanceTest;