import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
};

const payload = JSON.stringify({
    notify_teacher: true,
    notify_student: true,

    teacher: {
        name: "Test Teacher",
        email: "teacher@example.com"
    },

    students: Array.from({ length: 20 }, (_, i) => ({
        name: `Student ${i + 1}`,
        usn: `1MS22CS${String(i + 1).padStart(3, "0")}`,
        semester: "5",
        student_email: `student${i + 1}@example.com`,
        subjects: [
            {
                subject_name: "DBMS",
                attendance_percentage: 60,
                attended_classes: 18,
                total_classes: 30
            }
        ]
    }))
});

export default function () {
  const res = http.post(
    'http://localhost:8001/notify',
    payload,
    {
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  check(res, {
    'status is 200': (r) => r.status === 200,
});

console.log("Status:", res.status);
console.log("Body:", res.body);
}