import { motion, AnimatePresence } from 'framer-motion'
import { HiOutlineSparkles } from 'react-icons/hi2'
import { BsCheckCircleFill, BsXCircleFill } from 'react-icons/bs'
import { IoClose } from 'react-icons/io5'
import styles from './DownloadNotification.module.css'

/**
 * 우측 하단 다운로드 알림
 * - status: 'downloading' | 'complete' | 'error'
 * - downloading: 진행 바 + 스피너
 * - complete: 체크 아이콘 + 완료 메시지
 * - error: X 아이콘 + 에러 메시지
 * - 사용자가 X 버튼 눌러야 닫힘
 */
export default function DownloadNotification({ status, message, onClose }) {
  if (!status) return null

  const isDownloading = status === 'downloading'
  const isComplete = status === 'complete'
  const isError = status === 'error'

  const defaultMessage = isDownloading
    ? '다운로드 중...'
    : isComplete
      ? '다운이 완료되었어요!'
      : '다운로드에 실패했어요.'

  return (
    <AnimatePresence>
      <motion.div
        className={styles.wrapper}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        transition={{ duration: 0.25, ease: 'easeOut' }}
      >
        <div className={styles.row}>
          <div className={styles.iconWrap}>
            {isDownloading && <HiOutlineSparkles className={styles.sparkleIcon} />}
            {isComplete && <BsCheckCircleFill className={styles.completeIcon} />}
            {isError && <BsXCircleFill className={styles.errorIcon} />}
          </div>
          <span className={styles.message}>{message ?? defaultMessage}</span>
          <button className={styles.closeBtn} onClick={onClose} aria-label="닫기">
            <IoClose size={18} />
          </button>
        </div>
        {isDownloading && (
          <div className={styles.progressTrack}>
            <div className={styles.progressBar} />
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  )
}