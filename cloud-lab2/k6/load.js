import http from 'k6/http';
import { check, sleep } from 'k6';

const baseUrl = (__ENV.BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
const iterations = Number(__ENV.ITERATIONS || '1800000');
export const options = {
  stages: [
    { duration: '30s', target: 5 },
    { duration: '1m', target: 15 },
    { duration: '3m', target: 30 },
    { duration: '30s', target: 0 },
  ],
  thresholds: { http_req_failed: ['rate<0.05'] },
};

export default function () {
  const response = http.get(`${baseUrl}/compute?iterations=${iterations}&use_cache=false`,
    { timeout: '30s' });
  check(response, { 'HTTP 200': (r) => r.status === 200 });
  sleep(0.2);
}
