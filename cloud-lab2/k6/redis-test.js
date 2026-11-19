
import http from 'k6/http';
import { check, sleep } from 'k6';
import { options as originalOptions } from './load.js';

export const options = originalOptions;

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const USE_CACHE = __ENV.USE_CACHE || 'true';

export default function () {
    const response = http.get(
        `${BASE_URL}/notes?use_cache=${USE_CACHE}`
    );

    check(response, {
        'status is 200': (r) => r.status === 200,
    });

    sleep(1);
}
