import styles from './onNodeContext.module.css'

export default function ContextMenu({ x, y, node, onKeepToggle, onClose }) {
  const isKeep = node?.data?.keep ?? false

  return (
    <>
      <div className={styles.backdrop} onClick={onClose} />
      <div className={styles.menu} style={{ top: y, left: x }}>
        <span className={styles.title}>상태 변경</span>
        <button
          className={styles.option}
          onClick={() => { onKeepToggle(node.id); onClose() }}
        >
          <span className={styles.dot} />
          {isKeep ? 'keep 취소' : 'keep으로 변경'}
        </button>
      </div>
    </>
  )
}