import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProjects } from '../api/projects'

export default function ProjectListPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [viewMode, setViewMode] = useState('list')
  const [page, setPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const size = 20

  useEffect(() => {
    getProjects({ page, size }).then((data) => {
      setProjects(data.projects)
      setTotalCount(data.total_count)
    })
  }, [page])

  const totalPages = Math.max(1, Math.ceil(totalCount / size))

  return (
    <div>
      <div>
        <h2>모든 프로젝트</h2>
        <button onClick={() => setViewMode('grid')}>그리드</button>
        <button onClick={() => setViewMode('list')}>리스트</button>
      </div>

      {viewMode === 'list' ? (
        <table>
          <thead>
            <tr>
              <th>이름</th>
              <th>마지막으로 수정됨</th>
              <th>생성됨</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((p) => (
              <tr key={p.project_id} onClick={() => navigate(`/canvas/${p.project_id}`)}>
                <td>{p.name ?? '(이름 없음)'}</td>
                <td>{new Date(p.updated_at).toLocaleDateString()}</td>
                <td>{new Date(p.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div>
          {projects.map((p) => (
            <div key={p.project_id} onClick={() => navigate(`/canvas/${p.project_id}`)}>
              <strong>{p.name ?? '(이름 없음)'}</strong>
              <p>Stage {p.current_stage_number}</p>
            </div>
          ))}
        </div>
      )}

      <div>
        <button disabled={page === 1} onClick={() => setPage(page - 1)}>{'<'}</button>
        {Array.from({ length: totalPages }, (_, i) => (
          <button key={i + 1} onClick={() => setPage(i + 1)}>{i + 1}</button>
        ))}
        <button disabled={page === totalPages} onClick={() => setPage(page + 1)}>{'>'}</button>
      </div>

      <button onClick={() => navigate('/projects/create')}>프로젝트 생성하기 +</button>
    </div>
  )
}