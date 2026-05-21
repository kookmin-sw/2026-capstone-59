import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { HiOutlineFolder, HiOutlineTrash } from 'react-icons/hi'
import { HiOutlineUser } from 'react-icons/hi'
import styles from './ProjectListPage.module.css'
import { BsGrid, BsList, BsThreeDotsVertical, BsPencil, BsPlus, BsSearch, BsX } from 'react-icons/bs'
import { getProjects, deleteProject, updateProject } from '../api/projects'
import { getMe, logout } from '../api/auth'
import StepTreeThumbnail from '../components/StepTreeThumbnail'
import OnboardingTour from '../components/OnboardingTour'
import { useThumbnailTree } from '../hooks/useThumbnailTree'

function ProjectThumb({ project, variant = 'grid' }) {
  const { ref, data, isLoading } = useThumbnailTree(
    project.project_id,
    project.current_stage_sequence
  )
  const className = variant === 'grid' ? styles.cardThumb : styles.listThumb
  return (
    <div ref={ref} className={className}>
      <StepTreeThumbnail
        steps={data?.steps}
        stageSequence={project.current_stage_sequence}
        isLoading={isLoading}
      />
    </div>
  )
}

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
  const [sortBy, setSortBy] = useState('updated_at')
  const [keyword, setKeyword] = useState('')
  const [debouncedKeyword, setDebouncedKeyword] = useState('')
  const size = 8

  // 가장 최근 요청만 반영하기 위한 ID (stale 응답 차단)
  const requestIdRef = useRef(0)

  const [openMenuId, setOpenMenuId] = useState(null)
  const [infoModal, setInfoModal] = useState(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editData, setEditData] = useState({})
  const [deleteModal, setDeleteModal] = useState(null)
  const [toast, setToast] = useState(null)

  const [constraintInput, setConstraintInput] = useState('')
  const [editConstraints, setEditConstraints] = useState([])

  const [user, setUser] = useState(null)
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  const userWrapperRef = useRef(null)

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
    if (!openMenuId) return
    function handleClose(e) {
      if (!e.target.closest('[data-more-menu]')) {
        setOpenMenuId(null)
      }
    }
    document.addEventListener('mousedown', handleClose)
    return () => document.removeEventListener('mousedown', handleClose)
  }, [openMenuId])

  // 첫 진입 가이드 투어
  const [tourOpen, setTourOpen] = useState(false)
  useEffect(() => {
    const seen = localStorage.getItem('poco.tour.projectList')
    if (!seen) {
      // 페이지 렌더링 직후 살짝 지연시켜 자연스럽게 등장
      const t = setTimeout(() => setTourOpen(true), 600)
      return () => clearTimeout(t)
    }
  }, [])

  const handleTourClose = () => {
    setTourOpen(false)
    localStorage.setItem('poco.tour.projectList', '1')
  }

  const TOUR_STEPS = [
    {
      selector: `[data-tour="project-list-title"]`,
      title: '여기는 프로젝트 목록 화면이에요',
      body: '지금까지 만든 프로젝트가 여기에 모입니다. 이름·생성일 기준으로 정렬하거나 검색할 수 있어요.',
      placement: 'bottom',
    },
    {
      selector: `[data-tour="project-search"]`,
      title: '프로젝트 검색',
      body: '이름으로 빠르게 찾을 수 있어요. 입력하면 자동으로 필터링됩니다.',
      placement: 'bottom',
    },
    {
      selector: `[data-tour="project-view-toggle"]`,
      title: '보기 방식 변경',
      body: '카드형 / 리스트형으로 전환할 수 있어요. 취향대로 선택하세요.',
      placement: 'bottom',
    },
    {
      selector: `[data-tour="project-trash"]`,
      title: '휴지통',
      body: '삭제한 프로젝트는 휴지통으로 이동해요. 언제든 복원할 수 있습니다.',
      placement: 'right',
    },
    {
      selector: `[data-tour="project-create"]`,
      title: '새 프로젝트 시작하기',
      body: '버튼을 눌러 새 프로젝트를 만들면 Poco가 다음 한 걸음을 안내해드려요.',
      placement: 'top',
    },
  ]
  
  // 검색어 디바운싱 (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedKeyword(keyword.trim())
    }, 300)
    return () => clearTimeout(timer)
  }, [keyword])

  // 검색어가 바뀌면 첫 페이지로
  useEffect(() => {
    setPage(1)
  }, [debouncedKeyword])

  useEffect(() => {
    const params = { page, size, sort_by: sortBy, is_deleted: false }
    if (debouncedKeyword) params.keyword = debouncedKeyword

    const reqId = ++requestIdRef.current
    getProjects(params)
      .then((data) => {
        // 더 늦게 발사된 요청이 이미 응답에 반영됐다면 이 응답은 무시
        if (reqId !== requestIdRef.current) return
        setProjects(data.projects ?? [])
        setTotalCount(data.total_count ?? 0)
      })
      .catch(() => {})
  }, [page, sortBy, debouncedKeyword])

  useEffect(() => {
    getMe().then(setUser).catch(() => {})
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
    setConstraintInput('')
    setEditConstraints(project.constraints ?? [])
    setEditData({
      name: project.name ?? '',
      description: project.description ?? '',
    })
  }

  function handleAddModalConstraint() {
    const trimmed = constraintInput.trim()
    if (!trimmed || editConstraints.includes(trimmed)) return
    if (trimmed.length > 50) { showToast('제약 사항은 50자 이하로 입력해주세요.'); return }
    if (editConstraints.length >= 10) { showToast('제약 사항은 최대 10개까지 추가할 수 있어요.'); return }
    setEditConstraints([...editConstraints, trimmed])
    setConstraintInput('')
  }

  function handleCancelEdit() {
    setIsEditing(false)
    setConstraintInput('')
    setEditConstraints(infoModal.constraints ?? [])
    setEditData({
      name: infoModal.name ?? '',
      description: infoModal.description ?? '',
    })
  }

  function handleOpenDelete(e, project) {
    e.stopPropagation()
    setOpenMenuId(null)
    setDeleteModal(project)
  }

  function showToast(message) {
    setToast({ message })
    setTimeout(() => setToast(null), 5500)
  }

  async function handleSaveInfo() {
    try {
      const existingConstraints = infoModal.constraints ?? []
      const added = editConstraints.filter((c) => !existingConstraints.includes(c))

      await updateProject(infoModal.project_id, {
        name: editData.name || null,
        description: editData.description || null,
        new_constraints: added.length > 0 ? added : null,
      })
    } catch {
      showToast('수정에 실패했어요. 다시 시도해주세요.')
      return
    }

    setProjects(projects.map((p) =>
      p.project_id === infoModal.project_id
        ? { ...p, name: editData.name || null, description: editData.description || null, constraints: editConstraints }
        : p
    ))
    setInfoModal((prev) => ({ ...prev, name: editData.name || null, description: editData.description || null, constraints: editConstraints }))
    setIsEditing(false)
  }

  async function handleDelete() {
    try {
      await deleteProject(deleteModal.project_id)
    } catch {
      showToast('삭제에 실패했어요. 다시 시도해주세요.')
      return
    }

    const newTotalCount = totalCount - 1
    const newTotalPages = Math.max(1, Math.ceil(newTotalCount / size))

    setProjects(prev =>
      prev.filter((p) => p.project_id !== deleteModal.project_id)
    )
    setTotalCount(newTotalCount)
    setDeleteModal(null)

    if (page > newTotalPages) {
      setPage(newTotalPages)
    }

    showToast('1개의 프로젝트가 휴지통으로 이동했어요.')
  }

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <object data="/poco-logo-text.svg" alt="poco" height={25} onClick={() => navigate('/projects')}></object>
      </header>

      <div className={styles.body}>
        <aside className={styles.sidebar}>
          <nav className={styles.nav}>
            <button className={styles.navItemActive}>
              <HiOutlineFolder size={18} /> 모든 프로젝트
            </button>
            <button className={styles.navItem} onClick={() =>
              navigate('/projects/trash')}
              data-tour="project-trash"
            >
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
            <h2 className={styles.title} data-tour="project-list-title">모든 프로젝트</h2>
            <div className={styles.controls}>
              <div className={styles.searchBox} data-tour="project-search">
                <BsSearch className={styles.searchIcon} size={14} />
                <input
                  className={styles.searchInput}
                  type="text"
                  placeholder="프로젝트 검색"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                />
                {keyword && (
                  <button
                    type="button"
                    className={styles.searchClearBtn}
                    onClick={() => setKeyword('')}
                    aria-label="검색어 지우기"
                  >
                    <BsX size={16} />
                  </button>
                )}
              </div>
              <select className={styles.sortSelect} value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="updated_at">최근 사용일</option>
                <option value="created_at">생성일</option>
                <option value="name">이름</option>
              </select>
              <div className={styles.viewToggle} data-tour="project-view-toggle">
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

          {projects.length === 0 && debouncedKeyword ? (
            <div className={styles.emptyState}>
              <BsSearch size={28} className={styles.emptyIcon} />
              <p className={styles.emptyTitle}>검색 결과가 없어요</p>
              <p className={styles.emptyDesc}>
                <strong>"{debouncedKeyword}"</strong>와 일치하는 프로젝트가 없습니다.
              </p>
            </div>
          ) : viewMode === 'grid' ? (
            <div className={styles.grid}>
                {projects.length === 0 && (
                  <div className={styles.createCard} onClick={() => navigate('/projects/create')}>
                    <BsPlus size={32} color="var(--color-text-disabled)" />
                  </div>
                )}
              {sortedProjects.map((p) => (
                <div key={p.project_id} className={styles.card} onClick={() => navigate(`/canvas/${p.project_id}`, { state: { projectName: p.name ?? 'Project' } })}>
                  <ProjectThumb project={p} variant="grid" />
                  <div className={styles.cardInfo}>
                    <div>
                      <p className={styles.cardName}>{p.name ?? 'Project 1'}</p>
                      <p className={styles.cardMeta}>{timeAgo(p.updated_at)} 편집됨</p>
                    </div>
                    <div className={styles.moreWrapper} data-more-menu>
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
                      <ProjectThumb project={p} variant="list" />
                      {p.name ?? '(이름 없음)'}
                    </td>
                    <td>{timeAgo(p.updated_at)}</td>
                    <td>{new Date(p.created_at).toLocaleDateString()}</td>
                    <td>
                      <div className={styles.moreWrapper} data-more-menu>
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
            <button className={styles.createBtn} onClick={() => navigate('/projects/create')} data-tour="project-create">
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
              {/* 이름 */}
              <div className={`${styles.infoRow} ${styles.infoRowTop}`}>
                <span className={styles.infoLabel}>프로젝트 이름</span>
                {isEditing ? (
                  <div className={styles.infoEditCol}>
                    <input
                      className={styles.infoInput}
                      type="text"
                      maxLength={20}
                      value={editData.name ?? ''}
                      onChange={(e) => {
                        const value = e.target.value.slice(0, 20)
                        e.target.value = value
                        setEditData({ ...editData, name: value })
                      }}
                    />
                    <span className={styles.infoCharCount}>{(editData.name ?? '').length} / 20자</span>
                  </div>
                ) : (
                  <span className={styles.infoValue}>{infoModal.name || '-'}</span>
                )}
              </div>

              {/* 설명 */}
              <div className={`${styles.infoRow} ${styles.infoRowTop}`}>
                <span className={styles.infoLabel}>프로젝트 설명</span>
                {isEditing ? (
                  <div className={styles.infoEditCol}>
                    <input
                      className={styles.infoInput}
                      type="text"
                      maxLength={100}
                      value={editData.description ?? ''}
                      onChange={(e) => {
                        const value = e.target.value.slice(0, 100)
                        e.target.value = value
                        setEditData({ ...editData, description: value })
                      }}
                    />
                    <span className={styles.infoCharCount}>{(editData.description ?? '').length} / 100자</span>
                  </div>
                ) : (
                  <span className={styles.infoValue}>{infoModal.description || '-'}</span>
                )}
              </div>

              {/* 인원 - 잠김 */}
              <div className={styles.infoRow}>
                <span className={styles.infoLabel}>프로젝트 인원</span>
                <span className={`${styles.infoValue} ${isEditing ? styles.infoLocked : ''}`}>
                  {infoModal.member_count ? `${infoModal.member_count}명` : '-'}
                  {isEditing && <span className={styles.lockBadge}>🔒</span>}
                </span>
              </div>

              {/* 기간 - 잠김 */}
              <div className={styles.infoRow}>
                <span className={styles.infoLabel}>프로젝트 기간</span>
                <span className={`${styles.infoValue} ${isEditing ? styles.infoLocked : ''}`}>
                  {infoModal.duration_month === 0
                    ? '기간 없음'
                    : infoModal.duration_month
                    ? `약 ${infoModal.duration_month}개월`
                    : '-'}
                  {isEditing && <span className={styles.lockBadge}>🔒</span>}
                </span>
              </div>

              {/* 제약 사항 */}
              <div className={`${styles.infoRow} ${styles.infoRowTop}`}>
                <span className={styles.infoLabel}>제약 사항</span>
                <div className={styles.infoConstraintCol}>
                  {isEditing && (
                    <div className={styles.chipInputRow}>
                      <input
                        className={styles.infoInput}
                        type="text"
                        placeholder="제약 추가 후 Enter"
                        value={constraintInput}
                        onChange={(e) => setConstraintInput(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.nativeEvent.isComposing) {
                            e.preventDefault()
                            handleAddModalConstraint()
                          }
                        }}
                      />
                      <button type="button" className={styles.addChipBtn} onClick={handleAddModalConstraint}>
                        +
                      </button>
                    </div>
                  )}
                  {editConstraints.length > 0 && (
                    <div className={styles.chipList}>
                      {editConstraints.map((c, i) => (
                        <span key={i} className={styles.chip}>{c}</span>
                      ))}
                    </div>
                  )}
                  {!isEditing && editConstraints.length === 0 && (
                    <span className={styles.infoValue}>-</span>
                  )}
                </div>
              </div>
            </div>     
            <div className={styles.promptSection}>
              <p className={styles.promptLabel}>프로젝트 프롬프트</p>
              <p className={styles.promptText}>{infoModal.prompt ?? '-'}</p>
            </div>

            {isEditing && (
              <>
                <p className={styles.editInfoTip}>
                  💡 수정한 내용은 즉시 반영돼서, 다음에 만들어지는 Step부터 새 정보를 기반으로 추천돼요. 이전에 진행한 결정들은 그대로 보존되니 걱정하지 않으셔도 돼요!
                </p>
                <div className={styles.modalFooter}>
                  <button className={styles.cancelBtn} onClick={handleCancelEdit}>취소</button>
                  <button className={styles.saveBtn} onClick={handleSaveInfo}>저장</button>
                </div>
              </>
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

      {/* 토스트 알림 */}
      {toast && (
        <div className={styles.bottomToast}>
          {toast.message}
        </div>
      )}

      {/* 첫 진입 가이드 투어 */}
      <OnboardingTour
        steps={TOUR_STEPS}
        open={tourOpen}
        onClose={handleTourClose}
      />
    </div>
  )
}