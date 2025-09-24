"use client"
import React from 'react'
import SideBarIcon from './SideBarIcon'
import { FaBlog, FaInfoCircle, FaSignInAlt, FaSignOutAlt, FaUser } from 'react-icons/fa'

const SideNavbar = () => {
    const isLoggedIn = localStorage.getItem('access_token')
  return (
    <nav>
    <div className='sidebar-nav'>
        <SideBarIcon text='Profile' goto="/profile" icon={<FaUser size="28"/>}/>
        <SideBarIcon text='Create Post' goto="/create-post" icon={<FaBlog size="28"/>}/>
        <SideBarIcon text='About' goto="/about" icon={<FaInfoCircle size="28"/>}/>
        {isLoggedIn ? <SideBarIcon text="Sign out" goto="/signout" icon={<FaSignOutAlt size="28"/>}/> : <SideBarIcon text="Sign in" goto="/login" icon={<FaSignInAlt size="28"/>}/>}  
    </div>
    </nav>
  )
}

export default SideNavbar