import { motion, AnimatePresence } from 'framer-motion'
import { HiOutlineSparkles } from 'react-icons/hi2'
import { BsCheckCircleFill, BsXCircleFill, BsExclamationCircleFill } from 'react-icons/bs'
import { IoClose } from 'react-icons/io5'
import styles from './DownloadNotification.module.css'

/**
 * 우측 하단 다운로드 알림
 * - status: 'downloading' | 'complete' | 'error' | 'rate_limited'
 * - downloading: 진행 바 + 스피너
 * - complete:    체크 아이콘 + 완료 메시지
 * - error:       X 아이콘 + 에러 메시지
 * - rate_limited: 경고 아이콘 + 이미 진행 중 / 너무 잦은 요청 안내
 * - 사용자가 X 버튼 눌러야 닫힘
 */
export default function DownloadNotification({ status, message, onClose }) {
  if (!status) return null

  const isDownloading = status === 'downloading'
  const isComplete = status === 'complete'
  const isError = status === 'error'
  const isRateLimited = status === 'rate_limited'

  const defaultMessage = isDownloading
    ? '다운로드 중...'
    : isComplete
      ? '다운이 완료되었어요!'
      : isRateLimited
        ? '이미 다운로드가 진행 중이에요. 잠시 후 다시 시도해주세요.'
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
            {isRateLimited && <BsExclamationCircleFill className={styles.warnIcon} />}
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