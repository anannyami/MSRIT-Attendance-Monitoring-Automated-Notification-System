import http from "k6/http";
import { check } from "k6";

export const options = {
    vus: 20,
    duration: "30s",
};

export default function () {
    const res = http.get(
        "http://localhost:8000/students/1MS23CS001"
    );

    check(res, {
        "status is 200": (r) => r.status === 200,
    });
}