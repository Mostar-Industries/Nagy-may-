"use client"

import { useEffect, useState } from "react"
import type { Language } from "@/lib/i18n"

export function useI18n() {
  const [language, setLanguage] = useState<Language>("en")
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    // Get language from localStorage or browser preference
    const saved = localStorage.getItem("language") as Language | null
    const browserLang = navigator.language.split("-")[0] as Language

    const lang = saved || (browserLang in { en: 1, ha: 1, yo: 1, ig: 1, fr: 1 } ? browserLang : "en")
    setLanguage(lang)
    setMounted(true)
  }, [])

  const changeLanguage = (lang: Language) => {
    setLanguage(lang)
    localStorage.setItem("language", lang)
  }

  return { language, changeLanguage, mounted }
}
