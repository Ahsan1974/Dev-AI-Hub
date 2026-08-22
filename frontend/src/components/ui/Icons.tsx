import type { SVGProps } from 'react'

type IconProps = SVGProps<SVGSVGElement>

function Icon({ children, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      width="1em"
      height="1em"
      {...props}
    >
      {children}
    </svg>
  )
}

export const SearchIcon = (props: IconProps) => (
  <Icon {...props}>
    <circle cx="11" cy="11" r="7" />
    <path d="m20 20-3.2-3.2" />
  </Icon>
)

export const HeartIcon = ({ filled, ...props }: IconProps & { filled?: boolean }) => (
  <Icon fill={filled ? 'currentColor' : 'none'} {...props}>
    <path d="M12 20s-7-4.4-7-9.2A4 4 0 0 1 12 8a4 4 0 0 1 7 2.8C19 15.6 12 20 12 20Z" />
  </Icon>
)

export const CheckIcon = (props: IconProps) => (
  <Icon {...props}>
    <path d="m4.5 12.5 5 5 10-11" />
  </Icon>
)

export const CrossIcon = (props: IconProps) => (
  <Icon {...props}>
    <path d="M6 6l12 12M18 6 6 18" />
  </Icon>
)

export const WarnIcon = (props: IconProps) => (
  <Icon {...props}>
    <path d="M12 4.5 21 19H3l9-14.5Z" />
    <path d="M12 10v4" />
    <path d="M12 17h.01" />
  </Icon>
)

export const InfoIcon = (props: IconProps) => (
  <Icon {...props}>
    <circle cx="12" cy="12" r="8.5" />
    <path d="M12 11v5" />
    <path d="M12 8h.01" />
  </Icon>
)

export const ExternalIcon = (props: IconProps) => (
  <Icon {...props}>
    <path d="M14 5h5v5" />
    <path d="M19 5 10 14" />
    <path d="M18 14v4.5A1.5 1.5 0 0 1 16.5 20h-11A1.5 1.5 0 0 1 4 18.5v-11A1.5 1.5 0 0 1 5.5 6H10" />
  </Icon>
)

export const SunIcon = (props: IconProps) => (
  <Icon {...props}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6 7 7M17 17l1.4 1.4M18.4 5.6 17 7M7 17l-1.4 1.4" />
  </Icon>
)

export const MoonIcon = (props: IconProps) => (
  <Icon {...props}>
    <path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5Z" />
  </Icon>
)

export const MenuIcon = (props: IconProps) => (
  <Icon {...props}>
    <path d="M4 7h16M4 12h16M4 17h16" />
  </Icon>
)

export const FilterIcon = (props: IconProps) => (
  <Icon {...props}>
    <path d="M4 6h16M7 12h10M10 18h4" />
  </Icon>
)

export const ScaleIcon = (props: IconProps) => (
  <Icon {...props}>
    <path d="M12 4v16" />
    <path d="M5 8h14" />
    <path d="m5 8-2.5 6h5L5 8Z" />
    <path d="m19 8-2.5 6h5L19 8Z" />
  </Icon>
)

export const SparkIcon = (props: IconProps) => (
  <Icon {...props}>
    <path d="M12 4.5 13.6 9l4.4 1.6-4.4 1.6L12 16.5l-1.6-4.3L6 10.6 10.4 9 12 4.5Z" />
    <path d="M18.5 15.5 19.2 17l1.5.6-1.5.6-.7 1.4-.7-1.4L16.3 18l1.5-.6.7-1.4Z" />
  </Icon>
)

export const StackIcon = (props: IconProps) => (
  <Icon {...props}>
    <path d="m12 4 8 4-8 4-8-4 8-4Z" />
    <path d="m4 12 8 4 8-4" />
    <path d="m4 16 8 4 8-4" />
  </Icon>
)

export const GridIcon = (props: IconProps) => (
  <Icon {...props}>
    <rect x="4" y="4" width="7" height="7" rx="1.5" />
    <rect x="13" y="4" width="7" height="7" rx="1.5" />
    <rect x="4" y="13" width="7" height="7" rx="1.5" />
    <rect x="13" y="13" width="7" height="7" rx="1.5" />
  </Icon>
)

export const GiftIcon = (props: IconProps) => (
  <Icon {...props}>
    <rect x="3.5" y="9" width="17" height="11" rx="1.5" />
    <path d="M3.5 13h17M12 9v11" />
    <path d="M12 9C10.5 5.5 8.5 4 7.2 4.6 5.8 5.2 6.3 8 12 9Z" />
    <path d="M12 9c1.5-3.5 3.5-5 4.8-4.4C18.2 5.2 17.7 8 12 9Z" />
  </Icon>
)

export const ClockIcon = (props: IconProps) => (
  <Icon {...props}>
    <circle cx="12" cy="12" r="8.5" />
    <path d="M12 7.5V12l3 2" />
  </Icon>
)

export const ArrowRightIcon = (props: IconProps) => (
  <Icon {...props}>
    <path d="M5 12h13" />
    <path d="m13 6 6 6-6 6" />
  </Icon>
)

export const ShieldIcon = (props: IconProps) => (
  <Icon {...props}>
    <path d="M12 3.5 19 6v6c0 4-3 7-7 8.5C8 19 5 16 5 12V6l7-2.5Z" />
    <path d="m9 12 2 2 4-4" />
  </Icon>
)

const WORKFLOW_ICONS: Record<string, (props: IconProps) => JSX.Element> = {
  code: (props) => (
    <Icon {...props}>
      <path d="m9 8-4 4 4 4" />
      <path d="m15 8 4 4-4 4" />
    </Icon>
  ),
  bug: (props) => (
    <Icon {...props}>
      <rect x="8" y="7" width="8" height="12" rx="4" />
      <path d="M4 11h4M16 11h4M4 16h4M16 16h4M9 6 8 4M15 6l1-2" />
    </Icon>
  ),
  flask: (props) => (
    <Icon {...props}>
      <path d="M10 4v6l-5 8.5A1.5 1.5 0 0 0 6.3 21h11.4a1.5 1.5 0 0 0 1.3-2.5L14 10V4" />
      <path d="M9 4h6M7.5 15h9" />
    </Icon>
  ),
  check: (props) => <CheckIcon {...props} />,
  book: (props) => (
    <Icon {...props}>
      <path d="M5 5.5A1.5 1.5 0 0 1 6.5 4H19v13H6.5A1.5 1.5 0 0 0 5 18.5v-13Z" />
      <path d="M5 18.5A1.5 1.5 0 0 1 6.5 20H19" />
    </Icon>
  ),
  layout: (props) => (
    <Icon {...props}>
      <rect x="4" y="4" width="16" height="16" rx="2" />
      <path d="M4 9h16M10 9v11" />
    </Icon>
  ),
  search: (props) => <SearchIcon {...props} />,
  image: (props) => (
    <Icon {...props}>
      <rect x="4" y="5" width="16" height="14" rx="2" />
      <circle cx="9" cy="10" r="1.5" />
      <path d="m5 17 4.5-4.5L13 16l2.5-2.5L19 17" />
    </Icon>
  ),
  video: (props) => (
    <Icon {...props}>
      <rect x="3" y="6" width="12" height="12" rx="2" />
      <path d="m15 10 6-3v10l-6-3" />
    </Icon>
  ),
  audio: (props) => (
    <Icon {...props}>
      <path d="M4 10v4M8 7v10M12 4v16M16 8v8M20 11v2" />
    </Icon>
  ),
  rocket: (props) => (
    <Icon {...props}>
      <path d="M13.5 4.5c3 1 5 4 5 7l-3.5 3.5-4-4L14.5 7c-.3-1-.6-1.8-1-2.5Z" />
      <path d="m9 15-3 3M6 12l-2 2 2 2 2-2" />
      <path d="M12 18l2 2 2-2-2-2" />
    </Icon>
  ),
  graduation: (props) => (
    <Icon {...props}>
      <path d="m12 5 9 4-9 4-9-4 9-4Z" />
      <path d="M7 11.5V16c0 1.4 2.2 2.5 5 2.5s5-1.1 5-2.5v-4.5" />
    </Icon>
  ),
}

export function WorkflowIcon({ name, ...props }: IconProps & { name: string }) {
  const Component = WORKFLOW_ICONS[name] ?? GridIcon
  return <Component {...props} />
}
