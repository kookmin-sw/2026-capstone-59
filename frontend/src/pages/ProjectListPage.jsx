import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { HiOutlineFolder, HiOutlineTrash } from 'react-icons/hi'
import { HiOutlineUser } from 'react-icons/hi'
import styles from './ProjectListPage.module.css'
import { BsGrid, BsList, BsThreeDotsVertical, BsPencil, BsPlus } from 'react-icons/bs'

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

// TODO: 더미 데이터 — API 연동 후 제거
const DUMMY_PROJECTS = [
  {
    project_id: '1',
    name: '캡스톤 프로젝트',
    member_count: 3,
    duration_months: 2,
    description: '대학생 중고거래 플랫폼',
    constraint: '모바일 우선 개발',
    prompt: '현재 팀원 3명이서 2개월 동안 캡스톤 프로젝트를 진행해야해. 주제는 아직 정하지 않았지만 대학생과 관련한 걸로 하고 싶어.',
    updated_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(),
  },
  {
    project_id: '2',
    name: '포트폴리오 사이트',
    member_count: 1,
    duration_months: 1,
    description: '개인 포트폴리오 웹사이트',
    constraint: null,
    prompt: '1인 프로젝트로 개인 포트폴리오 사이트 만들고 싶어.',
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5).toISOString(),
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 60).toISOString(),
  },
  {
    project_id: '3',
    name: '쇼핑몰 앱',
    member_count: 4,
    duration_months: 6,
    description: '의류 쇼핑몰 모바일 앱',
    constraint: 'React Native 사용',
    prompt: '팀원 4명이서 6개월 동안 의류 쇼핑몰 앱을 만들고 싶어.',
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(),
  },
  {
    project_id: '4',
    name: null,
    member_count: 2,
    duration_months: 3,
    description: null,
    constraint: null,
    prompt: '팀원 2명이서 사이드 프로젝트 하고 싶어.',
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(),
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7).toISOString(),
  },
]

export default function ProjectListPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState(DUMMY_PROJECTS)
  const [viewMode, setViewMode] = useState('grid')
  const [page, setPage] = useState(1)
  const [totalCount, setTotalCount] = useState(DUMMY_PROJECTS.length)
  const [sortBy, setSortBy] = useState('updated_at')
  const size = 20

  const [openMenuId, setOpenMenuId] = useState(null)
  const [infoModal, setInfoModal] = useState(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editData, setEditData] = useState({})
  const [deleteModal, setDeleteModal] = useState(null)

  // TODO: API 연동 후 아래 주석 해제, 더미 데이터 및 초기값 제거
  // useEffect(() => {
  //   getProjects({ page, size }).then((data) => {
  //     setProjects(data.projects)
  //     setTotalCount(data.total_count)
  //   })
  // }, [page])

  useEffect(() => {
    function handleClickOutside(e) {
      if (!e.target.closest(`.${styles.moreWrapper}`)) {
        setOpenMenuId(null)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const sortedProjects = [...projects].sort((a, b) => {
    if (sortBy === 'updated_at') return new Date(b.updated_at) - new Date(a.updated_at)
    if (sortBy === 'created_at') return new Date(b.created_at) - new Date(a.created_at)
    if (sortBy === 'name') return (a.name ?? '').localeCompare(b.name ?? '')
  return 0
})

  const totalPages = Math.max(1, Math.ceil(totalCount / size))

  function handleMoreClick(e, projectId) {
    e.stopPropagation()
    setOpenMenuId(openMenuId === projectId ? null : projectId)
  }

  function handleOpenInfo(e, project) {
    e.stopPropagation()
    setOpenMenuId(null)
    setInfoModal(project)
    setIsEditing(false)
    setEditData({
      name: project.name ?? '',
      member_count: project.member_count ?? '',
      duration_months: project.duration_months ?? '',
      description: project.description ?? '',
      constraint: project.constraint ?? '',
    })
  }

  function handleOpenDelete(e, project) {
    e.stopPropagation()
    setOpenMenuId(null)
    setDeleteModal(project)
  }

  function handleSaveInfo() {
    // TODO: API 연동 후 실제 PATCH 호출로 교체
    setProjects(projects.map((p) =>
      p.project_id === infoModal.project_id
        ? { ...p, ...editData, name: editData.name || null }
        : p
    ))
    setIsEditing(false)
    setInfoModal(null)
  }

  function handleDelete() {
    // TODO: API 연동 후 실제 DELETE 호출로 교체
    setProjects(projects.filter((p) => p.project_id !== deleteModal.project_id))
    setTotalCount((prev) => prev - 1)
    setDeleteModal(null)
  }

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div className={styles.logo}onClick={() => navigate('/')}style={{ cursor: 'pointer' }}><span>poco</span></div>
      </header>

      <div className={styles.body}>
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

        <main className={styles.main}>
          <div className={styles.subHeader}>
            <h2 className={styles.title}>모든 프로젝트</h2>
            <div className={styles.controls}>
              <select className={styles.sortSelect} value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="updated_at">최근 사용일</option>
                <option value="created_at">생성일</option>
                <option value="name">이름</option>
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

          {viewMode === 'grid' ? (
            <div className={styles.grid}>
                {projects.length === 0 && (
                  <div className={styles.createCard} onClick={() => navigate('/projects/create')}>
                    <BsPlus size={32} color="var(--color-text-disabled)" />
                  </div>
                )}
              {sortedProjects.map((p) => (
                <div key={p.project_id} className={styles.card} onClick={() => navigate(`/canvas/${p.project_id}`)}>
                  <div className={styles.cardThumb} />
                  <div className={styles.cardInfo}>
                    <div>
                      <p className={styles.cardName}>{p.name ?? 'Project 1'}</p>
                      <p className={styles.cardMeta}>{timeAgo(p.updated_at)} 편집됨</p>
                    </div>
                    <div className={styles.moreWrapper}>
                      <button className={styles.moreBtn} onClick={(e) => handleMoreClick(e, p.project_id)}>
                        <BsThreeDotsVertical size={16} />
                      </button>
                      {openMenuId === p.project_id && (
                        <div className={styles.dropdown}>
                          <p className={styles.dropdownHeader}>프로젝트 편집</p>
                          <button className={styles.dropdownItem} onClick={(e) => handleOpenInfo(e, p)}>
                            프로젝트 정보
                          </button>
                          <button className={styles.dropdownItemDanger} onClick={(e) => handleOpenDelete(e, p)}>
                            프로젝트 삭제
                          </button>
                        </div>
                      )}
                    </div>
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
                {sortedProjects.map((p) => (
                  <tr key={p.project_id} onClick={() => navigate(`/canvas/${p.project_id}`)}>
                    <td>
                      <div className={styles.listThumb} />
                      {p.name ?? '(이름 없음)'}
                    </td>
                    <td>{timeAgo(p.updated_at)}</td>
                    <td>{new Date(p.created_at).toLocaleDateString()}</td>
                    <td>
                      <div className={styles.moreWrapper}>
                        <button className={styles.moreBtn} onClick={(e) => handleMoreClick(e, p.project_id)}>
                          <BsThreeDotsVertical size={16} />
                        </button>
                        {openMenuId === p.project_id && (
                          <div className={styles.dropdown}>
                            <p className={styles.dropdownHeader}>프로젝트 편집</p>
                            <button className={styles.dropdownItem} onClick={(e) => handleOpenInfo(e, p)}>
                              프로젝트 정보
                            </button>
                            <button className={styles.dropdownItemDanger} onClick={(e) => handleOpenDelete(e, p)}>
                              프로젝트 삭제
                            </button>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

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

      {/* 프로젝트 정보 모달 */}
      {infoModal && (
        <div className={styles.overlay} onClick={() => { setInfoModal(null); setIsEditing(false) }}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <div className={styles.modalTitle}>
                프로젝트 정보
                <button
                  className={`${styles.editToggleBtn} ${isEditing ? styles.editToggleBtnActive : ''}`}
                  onClick={() => setIsEditing(!isEditing)}
                >
                  <BsPencil size={13} />
                </button>
              </div>
              <button className={styles.closeBtn} onClick={() => { setInfoModal(null); setIsEditing(false) }}>✕</button>
            </div>

            <div className={styles.infoTable}>
              {[
                { label: '프로젝트 이름', key: 'name', type: 'input' },
                { label: '프로젝트 인원', key: 'member_count', type: 'input', inputType: 'number', suffix: '명' },
                { label: '프로젝트 기간', key: 'duration_months', type: 'input', inputType: 'number', suffix: '개월' },
                { label: '프로젝트 설명', key: 'description', type: 'textarea' },
                { label: '프로젝트 제약 사항', key: 'constraint', type: 'textarea' },
              ].map(({ label, key, type, inputType, suffix }) => (
                <div key={key} className={styles.infoRow}>
                  <span className={styles.infoLabel}>{label}</span>
                  {isEditing ? (
                    type === 'textarea' ? (
                      <textarea
                        className={styles.infoTextarea}
                        value={editData[key] ?? ''}
                        onChange={(e) => setEditData({ ...editData, [key]: e.target.value })}
                      />
                    ) : (
                      <input
                        className={styles.infoInput}
                        type={inputType ?? 'text'}
                        value={editData[key] ?? ''}
                        onChange={(e) => setEditData({ ...editData, [key]: e.target.value })}
                      />
                    )
                  ) : (
                    <span className={styles.infoValue}>
                      {infoModal[key] ? `${infoModal[key]}${suffix ?? ''}` : '-'}
                    </span>
                  )}
                </div>
              ))}
            </div>

            <div className={styles.promptSection}>
              <p className={styles.promptLabel}>프로젝트 프롬프트</p>
              <p className={styles.promptText}>{infoModal.prompt ?? '-'}</p>
            </div>

            {isEditing && (
              <div className={styles.modalFooter}>
                <button className={styles.cancelBtn} onClick={() => setIsEditing(false)}>취소</button>
                <button className={styles.saveBtn} onClick={handleSaveInfo}>저장</button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 삭제 확인 모달 */}
      {deleteModal && (
        <div className={styles.overlay} onClick={() => setDeleteModal(null)}>
          <div className={styles.deleteModal} onClick={(e) => e.stopPropagation()}>
            <p className={styles.deleteTitle}>프로젝트를 삭제하시겠습니까?</p>
            <p className={styles.deleteDesc}>
              삭제된 프로젝트는 30일 간 휴지통에 보관되며 이후 영구히 삭제됩니다.
            </p>
            <div className={styles.deleteActions}>
              <button className={styles.cancelBtn} onClick={() => setDeleteModal(null)}>취소</button>
              <button className={styles.deleteBtn} onClick={handleDelete}>삭제</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}