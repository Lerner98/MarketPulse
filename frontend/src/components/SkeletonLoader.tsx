interface SkeletonLoaderProps {
  className?: string
  variant?: 'text' | 'rectangular' | 'circular'
  width?: string
  height?: string
}

function SkeletonLoader({
  className = '',
  variant = 'rectangular',
  width,
  height,
}: SkeletonLoaderProps) {
  const variantClasses = {
    text: 'rounded',
    rectangular: 'rounded-lg',
    circular: 'rounded-full',
  }

  const style = {
    width: width || (variant === 'circular' ? '40px' : '100%'),
    height: height || (variant === 'text' ? '1em' : '40px'),
  }

  return (
    <div
      className={`bg-gray-200 animate-pulse ${variantClasses[variant]} ${className}`}
      style={style}
      aria-busy="true"
      aria-live="polite"
    />
  )
}

export default SkeletonLoader
