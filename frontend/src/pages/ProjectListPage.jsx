import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProjects } from '../api/projects'
import { BsGrid, BsList, BsThreeDotsVertical, BsPlus } from 'react-icons/bs'
import { HiOutlineFolder, HiOutlineTrash } from 'react-icons/hi'
import { HiOutlineUser } from 'react-icons/hi'
import styles from './ProjectListPage.module.css'

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  if (minutes < 1) return '방금 전'
  if (minutes < 60) return `${minutes}분 전`
  if (hours < 24) return `${hours}시간 전`
  return `${days}일 전`
}

export default function ProjectListPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [viewMode, setViewMode] = useState('grid')
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
    <div className={styles.layout}>
      {/* 상단 헤더 - 전체 너비 */}
      <header className={styles.header}>
        <div className={styles.logo}>
          <span>poco</span>
        </div>
      </header>

      <div className={styles.body}>
        {/* 사이드바 */}
        <aside className={styles.sidebar}>
          <nav className={styles.nav}>
            <button className={styles.navItemActive}>
              <HiOutlineFolder size={18} /> 모든 프로젝트
            </button>
            <button className={styles.navItem}>
              <HiOutlineTrash size={18} /> 휴지통
            </button>
          </nav>
          <div className={styles.user}>
            <HiOutlineUser size={20} />
            <span>User</span>
          </div>
        </aside>

        {/* 메인 */}
        <main className={styles.main}>
          {/* 서브 헤더 */}
          <div className={styles.subHeader}>
            <h2 className={styles.title}>모든 프로젝트</h2>
            <div className={styles.controls}>
              <select className={styles.sortSelect}>
                <option>최근 사용일</option>
                <option>생성일</option>
                <option>이름</option>
              </select>
              <div className={styles.viewToggle}>
              <button
                className={viewMode === 'grid' ? styles.viewBtnActive : styles.viewBtn}
                onClick={() => setViewMode('grid')}
              >
                <BsGrid size={18} />
              </button>
              <button
                className={viewMode === 'list' ? styles.viewBtnActive : styles.viewBtn}
                onClick={() => setViewMode('list')}
              >
                <BsList size={18} />
              </button>
            </div>
            </div>
          </div>

          {/* 프로젝트 목록 */}
          {viewMode === 'grid' ? (
            <div className={styles.grid}>
              <div className={styles.createCard} onClick={() => navigate('/projects/create')}>
                <BsPlus size={32} color="var(--color-text-disabled)" />
              </div>
              {projects.map((p) => (
                <div key={p.project_id} className={styles.card} onClick={() => navigate(`/canvas/${p.project_id}`)}>
                  <div className={styles.cardThumb} />
                  <div className={styles.cardInfo}>
                    <div>
                      <p className={styles.cardName}>{p.name ?? '(이름 없음)'}</p>
                      <p className={styles.cardMeta}>{timeAgo(p.updated_at)} 전 편집됨</p>
                    </div>
                    <button className={styles.moreBtn} onClick={(e) => e.stopPropagation()}>
                      <BsThreeDotsVertical size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>이름</th>
                  <th>마지막으로 수정됨</th>
                  <th>생성됨</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => (
                  <tr key={p.project_id} onClick={() => navigate(`/canvas/${p.project_id}`)}>
                    <td>
                      <div className={styles.listThumb} />
                      {p.name ?? '(이름 없음)'}
                    </td>
                    <td>{timeAgo(p.updated_at)}</td>
                    <td>{new Date(p.created_at).toLocaleDateString()}</td>
                    <td>
                      <button className={styles.moreBtn} onClick={(e) => e.stopPropagation()}>
                        <BsThreeDotsVertical size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {/* 하단 */}
          <div className={styles.footer}>
            <button className={styles.createBtn} onClick={() => navigate('/projects/create')}>
              프로젝트 생성하기 <span>+</span> 
            </button>
            <div className={styles.pagination}>
              <button disabled={page === 1} onClick={() => setPage(page - 1)}>{'<'}</button>
              {Array.from({ length: totalPages }, (_, i) => (
                <button
                  key={i + 1}
                  className={page === i + 1 ? styles.pageActive : styles.pageBtn}
                  onClick={() => setPage(i + 1)}
                >
                  {i + 1}
                </button>
              ))}
              <button disabled={page === totalPages} onClick={() => setPage(page + 1)}>{'>'}</button>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}