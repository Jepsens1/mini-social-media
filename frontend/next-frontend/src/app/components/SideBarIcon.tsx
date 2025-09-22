import Link from 'next/link'
import React from 'react'

const SideBarIcon = ({ icon, text = 'tooltip', goto}) => {
  return (
    <div className='sidebar-icon group'>
        <Link href={goto}>
            {icon}
        </Link>
        <span className='sidebar-tooltip group-hover:scale-100'>
            {text}
        </span>
    </div>
  )
}

export default SideBarIcon