import http from 'k6/http';
import { check, sleep } from 'k6';

const baseUrl = (__ENV.BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
const iterations = Number(__ENV.ITERATIONS || '1000000');
const cache = (__ENV.CACHE || 'true').toLowerCase() === 'true';
export const options = {
  vus: 3,
  duration: '30s',
  thresholds: { http_req_failed: ['rate<0.01'] },
};

export default function () {
  const response = http.get(`${baseUrl}/compute?iterations=${iterations}&use_cache=${cache}`);
  check(response, { 'HTTP 200': (r) => r.status === 200 });
  sleep(0.1);
}
