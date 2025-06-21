"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { ChevronRight, Home } from "lucide-react"

export function Breadcrumb() {
  const pathname = usePathname()

  const pathSegments = pathname.split("/").filter(Boolean)

  const breadcrumbItems = [
    { href: "/", label: "Home", icon: Home },
    ...pathSegments.map((segment, index) => {
      const href = "/" + pathSegments.slice(0, index + 1).join("/")
      const label = segment.charAt(0).toUpperCase() + segment.slice(1)
      return { href, label }
    }),
  ]

  if (pathname === "/") return null

  return (
    <nav className="bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-700">
      <div className="container mx-auto px-4 py-3">
        <ol className="flex items-center space-x-2 text-sm">
          {breadcrumbItems.map((item, index) => {
            const isLast = index === breadcrumbItems.length - 1
            const Icon = item.icon

            return (
              <li key={item.href} className="flex items-center">
                {index > 0 && <ChevronRight className="w-4 h-4 text-gray-400 mx-2" />}
                {isLast ? (
                  <span className="flex items-center text-gray-900 dark:text-white font-medium">
                    {Icon && <Icon className="w-4 h-4 mr-2" />}
                    {item.label}
                  </span>
                ) : (
                  <Link
                    href={item.href}
                    className="flex items-center text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                  >
                    {Icon && <Icon className="w-4 h-4 mr-2" />}
                    {item.label}
                  </Link>
                )}
              </li>
            )
          })}
        </ol>
      </div>
    </nav>
  )
}
