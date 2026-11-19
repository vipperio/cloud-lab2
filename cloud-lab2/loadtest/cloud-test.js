import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL;
const USE_CACHE = __ENV.USE_CACHE || 'true';
const N = Number(__ENV.VUS || 30);

export const options = {
    stages: [
        { duration: '3m', target: N },
        { duration: '5m', target: N },
        { duration: '2m', target: 0 },
    ],
    summaryTrendStats: [
        'avg', 'min', 'med', 'max',
        'p(50)', 'p(90)', 'p(95)', 'p(99)'
    ],
};

export default function () {
    const payload = JSON.stringify({
        title: `Note-${__VU}-${__ITER}`,
        content: 'Cloud load testing'
    });

    const created = http.post(
        `${BASE_URL}/notes`,
        payload,
        {
            headers: {
                'Content-Type': 'application/json'
            }
        }
    );

    const success = check(created, {
        'note created': r =>
            r.status === 200 || r.status === 201
    });

    let noteId = 1;

    if (success) {
        noteId = created.json('id') || 1;
    }

    for (let i = 0; i < 9; i++) {
        const endpoint = i === 8
            ? `/notes/${noteId}`
            : `/notes?use_cache=${USE_CACHE}`;

        const response = http.get(
            `${BASE_URL}${endpoint}`
        );

        check(response, {
            'read successful': r => r.status === 200
        });
    }

    sleep(1);
}
