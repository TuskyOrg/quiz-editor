db.createUser(
    {
        user: "admin",
        pwd: "example",
        roles: [
            {
                role: "readWrite",
                db: "quiz"
            }
        ]
    }
)

// Constraint ensuring two active rooms cannot share the same room code
// (Model in app/models.py). Unfortunately, it doesn't work yet.
db.quiz.createIndex(
    { code: 1 },
    { unique: true, partialFilterExpression: { is_active: true } }
)
