# UPSC Study OS Agent - Quick Reference

## 🚀 Quick Start

### Invoke the Agent
```
/upsc-study-os-agent
```

Then describe your task:
```
Create a new feature for [module name]
Fix the bug in [component/service]
Add the [feature] to [module]
```

## 📋 Common Tasks

### Create a New Feature
```
Tasks the agent will handle:
1. Design backend models and schemas
2. Create FastAPI endpoints
3. Generate Angular components
4. Connect frontend to backend
5. Write tests
6. Update documentation
```

### Fix a Bug
```
Agent will:
1. Locate and understand the issue
2. Find root cause
3. Implement fix
4. Write regression tests
5. Verify no side effects
6. Document the fix
```

### Optimize Performance
```
Agent will:
1. Identify bottlenecks
2. Create indexes if needed
3. Optimize queries
4. Add caching
5. Benchmark improvements
6. Deploy changes
```

## 🛠️ Agent Capabilities

| Task | Capability | ✓ |
|------|-----------|---|
| Backend API | Create FastAPI endpoints | ✓ |
| Frontend UI | Generate Angular components | ✓ |
| Database | Create migrations, manage schema | ✓ |
| Testing | Write and run tests | ✓ |
| AI Integration | Handle OpenAI, embeddings, OCR | ✓ |
| Authentication | JWT, OAuth implementation | ✓ |
| Deployment | Prepare configs, manage secrets | ✓ |
| Documentation | Update API docs, comments | ✓ |

## 📁 Project Structure

```
upsc-study-os/
├── frontend/          → Angular 19 application
├── backend/           → FastAPI application
└── .github/agents/    → Custom agent configurations
```

## 🔧 Development Workflow

### Backend
```python
1. Model      → backend/app/models/
2. Schema     → backend/app/schemas/
3. Route      → backend/app/api/routes/
4. Migration  → alembic upgrade head
5. Test       → pytest tests/
```

### Frontend
```typescript
1. Component  → ng generate component
2. Service    → ng generate service
3. Routing    → Update app-routing.module.ts
4. Styling    → Tailwind CSS
5. Test       → ng test
```

## 📚 Modules

1. **Authentication** - JWT + Google OAuth
2. **Dashboard** - User profile & overview
3. **Subjects** - Topic hierarchy
4. **PYQ Analyzer** - Previous year questions
5. **AI Mentor** - GPT-powered tutoring
6. **Smart Notes** - Note management
7. **Revision** - Spaced repetition
8. **Planner** - Daily schedules
9. **Current Affairs** - News linking
10. **Evaluation** - Answer grading
11. **Analytics** - Performance tracking
12. **Admin** - System management

## 💡 Key Commands

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
ng serve
```

### Database
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

### Testing
```bash
cd backend
pytest tests/ -v
```

## 🎯 Success Checklist

- [ ] Code follows conventions
- [ ] Tests pass
- [ ] No console errors
- [ ] Documentation updated
- [ ] Feature working correctly
- [ ] Integration verified
- [ ] Performance acceptable
- [ ] Security considered

## 🤖 Agent Intelligence

The agent automatically:
- ✓ Understands project structure
- ✓ Follows code conventions
- ✓ Handles errors gracefully
- ✓ Writes tests
- ✓ Validates implementations
- ✓ Learns from patterns
- ✓ Self-modifies approach
- ✓ Documents changes

## 🔒 Security Built-in

The agent ensures:
- Input validation
- Proper authentication
- Authorization checks
- Secure API design
- Password hashing
- Environment variable security
- CORS configuration
- Rate limiting

## 📈 Performance Aware

The agent optimizes:
- Database queries
- API response times
- Frontend bundle size
- Caching strategies
- Index creation
- Query optimization

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | Check DATABASE_URL, PostgreSQL running |
| Frontend won't build | npm ci, check Angular version |
| Tests failing | Run with -v flag, check fixtures |
| API call fails | Check backend running, CORS config |
| Migration fails | Review migration, check syntax |

## 📞 Getting Help

1. Check `AGENTS.md` for detailed agent instructions
2. Review `AGENT_SETUP.md` for comprehensive setup guide
3. Check project README for quick start
4. Review DEPLOYMENT.md for deployment help

## 💾 File Locations

| File | Purpose |
|------|---------|
| `.github/agents/upsc-study-os-agent.agent.md` | Agent definition |
| `.github/instructions/upsc-project.instructions.md` | Project context |
| `AGENTS.md` | Agent development guide |
| `AGENT_SETUP.md` | Setup documentation |
| `README.md` | Project overview |
| `DEPLOYMENT.md` | Deployment guide |

## 🎓 Learning Resources

The agent has been trained on:
- Project architecture and design
- Development patterns and conventions
- Module structure and responsibilities
- Testing strategies
- Deployment processes
- Security best practices
- Performance optimization techniques

## ⚡ Quick Tips

1. **Be Specific** - Provide clear task descriptions
2. **Include Context** - Reference related files
3. **Set Expectations** - What should the result include?
4. **Review Results** - Always check agent output
5. **Iterate** - Provide feedback for refinements

## 🔄 Continuous Learning

The agent improves over time by:
- Documenting new patterns
- Recording solutions
- Sharing optimizations
- Updating best practices
- Learning from your feedback

## 📝 Example Tasks

```
"Add email notifications to the revision system"
"Optimize the AI mentor embeddings search"
"Create an admin panel for user management"
"Fix the daily planner time calculation bug"
"Implement batch processing for OCR documents"
```

## 🏁 Ready to Use

Your autonomous agent is ready to:
1. ✅ Understand complex requirements
2. ✅ Design comprehensive solutions
3. ✅ Implement full-stack features
4. ✅ Test thoroughly
5. ✅ Document properly
6. ✅ Deploy confidently
7. ✅ Learn and adapt
8. ✅ Self-improve continuously

**Start by invoking: `/upsc-study-os-agent`**

---

**Happy Development! 🚀**

For detailed information, see:
- AGENT_SETUP.md (comprehensive guide)
- AGENTS.md (development instructions)
- README.md (project overview)
