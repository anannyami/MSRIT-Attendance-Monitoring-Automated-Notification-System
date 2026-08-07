import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 20,
  duration: '30s',
};

export default function () {
  const payload = JSON.stringify({
    email: "teacher@example.com",
    password: "password"
  });

  const params = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  const res = http.post(
    "http://localhost:8000/login",
    payload,
    params
  );

  check(res, {
    "status is 200": (r) => r.status === 200,
  });
}