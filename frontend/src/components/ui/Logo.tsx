export function Logo() {
  return (
    <span className="inline-flex items-center gap-1.5">
      <svg
        width="20"
        height="20"
        viewBox="0 0 36 36"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M6 10a6 6 0 0 1 6-6h12a6 6 0 0 1 6 6v10a6 6 0 0 1-6 6H15l-6.5 5.2c-.7.56-1.75.06-1.75-.84V26a6 6 0 0 1-.75-.12A6 6 0 0 1 6 20V10Z"
          fill="var(--color-primary)"
        />
        <text
          x="18"
          y="21"
          textAnchor="middle"
          fontFamily="Pretendard, -apple-system, sans-serif"
          fontSize="15"
          fontWeight="800"
          fill="#fff"
        >
          ?
        </text>
      </svg>
      <span className="text-[15px] font-semibold tracking-[-0.02em] text-ink">
        혹시
      </span>
    </span>
  );
}
