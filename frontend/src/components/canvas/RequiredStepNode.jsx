import { Handle, Position } from '@xyflow/react'
import styles from './RequiredStepNode.module.css'

export default function RequiredStepNode({ data }) {
  const { label, step_id } = data

  return (
    <div className={styles.wrapper}>
      <Handle type="target" position={Position.Left} style={{ opacity: 0, left: 20, top: '48%' }} />
      <svg xmlns="http://www.w3.org/2000/svg" width="192" height="140" viewBox="0 0 192 140" fill="none">
        <g filter={`url(#f-${step_id})`}>
          <path d="M21.4411 74.2794C14.8481 70.4128 14.8542 60.8793 21.452 57.0211L95.2474 13.8676C98.3696 12.0418 102.234 12.0443 105.354 13.874L179.385 57.2911C185.978 61.1577 185.972 70.6912 179.374 74.5494L105.579 117.703C102.457 119.529 98.5918 119.526 95.4719 117.696L21.4411 74.2794Z" fill={`url(#g-${step_id})`}/>
          <path d="M21.4411 74.2794C14.8481 70.4128 14.8542 60.8793 21.452 57.0211L95.2474 13.8676C98.3696 12.0418 102.234 12.0443 105.354 13.874L179.385 57.2911C185.978 61.1577 185.972 70.6912 179.374 74.5494L105.579 117.703C102.457 119.529 98.5918 119.526 95.4719 117.696L21.4411 74.2794Z" stroke="#C5BDFB"/>
        </g>
        <defs>
          <filter id={`f-${step_id}`} x="0" y="0" width="200.826" height="139.571" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
            <feFlood floodOpacity="0" result="BackgroundImageFix"/>
            <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
            <feOffset dy="4"/>
            <feGaussianBlur stdDeviation="8"/>
            <feComposite in2="hardAlpha" operator="out"/>
            <feColorMatrix type="matrix" values="0 0 0 0 0.360784 0 0 0 0 0.270588 0 0 0 0 0.909804 0 0 0 0.11 0"/>
            <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow"/>
            <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow" result="shape"/>
          </filter>
          <linearGradient id={`g-${step_id}`} x1="166.913" y1="93.1317" x2="39.4517" y2="103.913" gradientUnits="userSpaceOnUse">
            <stop stopColor="#6F60FF"/>
            <stop offset="1" stopColor="#A19AFF"/>
          </linearGradient>
        </defs>
      </svg>
      {status === 'ACCEPTED' && <div className={styles.dot} />}
      <span className={styles.label}>{label}</span>
      <Handle type="source" position={Position.Right} style={{ opacity: 0, right: 15, top: '48%' }} />
    </div>
  )
}