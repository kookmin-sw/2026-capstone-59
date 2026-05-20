import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { HiOutlineFolder, HiOutlineTrash } from 'react-icons/hi'
import { HiOutlineUser } from 'react-icons/hi'
import { BsGrid, BsList } from 'react-icons/bs'
import { MdOutlineSettingsBackupRestore } from "react-icons/md";
import styles from './ProjectListPage.module.css'
import { getProjects, restoreProject } from '../api/projects'
import { getMe, logout } from '../api/auth'

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

export default function TrashPage() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [projects, setProjects] = useState([])
  const [viewMode, setViewMode] = useState('grid')
  const [page, setPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const [toast, setToast] = useState(null)
  const userWrapperRef = useRef(null)
  const size = 8

  useEffect(() => {
    if (!userMenuOpen) return
    function handleClickOutside(e) {
      if (userWrapperRef.current && !userWrapperRef.current.contains(e.target)) {
        setUserMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [userMenuOpen])

  useEffect(() => {
    getProjects({ page, size, is_deleted: true }).then((data) => {
      setProjects(data.projects ?? [])
      setTotalCount(data.total_count ?? 0)
    })
    }, [page, size])

  useEffect(() => {
    getMe().then(setUser).catch(() => {})
  }, [])

  const totalPages = Math.max(1, Math.ceil(totalCount / size))

  function showToast(message) {
    setToast({ message })
    setTimeout(() => setToast(null), 5500)
  }

  async function handleRestore(e, projectId) {
    e.stopPropagation()
    try {
      await restoreProject(projectId)
    } catch {
      showToast('복원에 실패했어요. 다시 시도해주세요.')
      return
    }

    const newTotalCount = totalCount - 1
    const newTotalPages = Math.max(1, Math.ceil(newTotalCount / size))

    setProjects(prev => prev.filter((p) => p.project_id !== projectId))
    setTotalCount(newTotalCount)

    if (page > newTotalPages) {
      setPage(newTotalPages)
    }

    showToast('1개의 프로젝트가 복원됐어요.')
  }

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <img src="/poco-logo-text.svg" alt="poco" height={25} onClick={() => navigate('/projects')}/>
      </header>

      <div className={styles.body}>
        <aside className={styles.sidebar}>
          <nav className={styles.nav}>
            <button className={styles.navItem} onClick={() => navigate('/projects')}>
              <HiOutlineFolder size={18} /> 모든 프로젝트
            </button>
            <button className={styles.navItemActive}>
              <HiOutlineTrash size={18} /> 휴지통
            </button>
          </nav>
          <div className={styles.userWrapper} ref={userWrapperRef}>
            <button
              className={styles.userBtn}
              onClick={() => setUserMenuOpen((v) => !v)}
            >
              <HiOutlineUser size={18} />
            </button>
            {userMenuOpen && (
              <div className={styles.userDropdown}>
                <p className={styles.userEmail}>{user?.email ?? '-'}</p>
                <button
                  className={styles.logoutBtn}
                  onClick={async () => {
                    await logout()
                    navigate('/')
                  }}
                >
                  로그아웃
                </button>
              </div>
            )}
          </div>
        </aside>

        <main className={styles.main}>
          <div className={styles.subHeader}>
            <h2 className={styles.title}>휴지통</h2>
            <div className={styles.controls}>
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

          {viewMode === 'grid' ? (
            <div className={styles.grid}>
              {projects.length === 0 && (
                <p style={{ color: 'var(--color-text-disabled)', fontSize: 14 }}>
                  휴지통이 비어있어요.
                </p>
              )}
              {projects.map((p) => (
                <div key={p.project_id} className={styles.card}>
                  <div className={styles.cardThumb} />
                  <div className={styles.cardInfo}>
                    <div>
                      <p className={styles.cardName}>{p.name}</p>
                      <p className={styles.cardMeta}>{timeAgo(p.updated_at)} 삭제됨</p>
                    </div>
                    <button
                      className={styles.moreBtn}
                      onClick={(e) => handleRestore(e, p.project_id)}
                      title="복원"
                    >
                      <MdOutlineSettingsBackupRestore size={20} />
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
                  <th>삭제됨</th>
                  <th>생성됨</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => (
                  <tr key={p.project_id}>
                    <td>
                      <div className={styles.listThumb} />
                      {p.name}
                    </td>
                    <td>{timeAgo(p.updated_at)}</td>
                    <td>{new Date(p.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        className={styles.moreBtn}
                        onClick={(e) => handleRestore(e, p.project_id)}
                        title="복원"
                      >
                        <MdOutlineSettingsBackupRestore size={20} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <div className={styles.footer}>
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
      {toast && (
      <div className={styles.bottomToast}>
        {toast.message}
      </div>
    )}
    </div>
  )
}