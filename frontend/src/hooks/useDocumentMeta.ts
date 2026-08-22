import { useEffect } from 'react'

interface DocumentMeta {
  title: string
  description?: string
  /** JSON-LD injected for tool and collection pages. */
  structuredData?: Record<string, unknown> | null
}

const SITE = 'DevAI Hub'
const STRUCTURED_DATA_ID = 'devai-hub-structured-data'

function setMetaTag(selector: string, attribute: string, name: string, content: string) {
  let tag = document.head.querySelector<HTMLMetaElement>(selector)
  if (!tag) {
    tag = document.createElement('meta')
    tag.setAttribute(attribute, name)
    document.head.appendChild(tag)
  }
  tag.setAttribute('content', content)
}

/** Sets title, description and OpenGraph tags for the current route. */
export function useDocumentMeta({ title, description, structuredData }: DocumentMeta): void {
  useEffect(() => {
    const fullTitle = title === SITE ? title : `${title} — ${SITE}`
    document.title = fullTitle
    setMetaTag('meta[property="og:title"]', 'property', 'og:title', fullTitle)
    setMetaTag('meta[property="og:url"]', 'property', 'og:url', window.location.href)

    if (description) {
      setMetaTag('meta[name="description"]', 'name', 'description', description)
      setMetaTag('meta[property="og:description"]', 'property', 'og:description', description)
    }
  }, [title, description])

  useEffect(() => {
    document.getElementById(STRUCTURED_DATA_ID)?.remove()
    if (!structuredData) return

    const script = document.createElement('script')
    script.type = 'application/ld+json'
    script.id = STRUCTURED_DATA_ID
    script.textContent = JSON.stringify(structuredData)
    document.head.appendChild(script)

    return () => script.remove()
  }, [structuredData])
}
