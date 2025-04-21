import { forwardRef } from "react";
import { NavLink, Link } from "react-router-dom";

import { navbarLinks } from "@/constants";

import logoLight from "@/assets/logo-light.svg";
import logoDark from "@/assets/logo-dark.svg";

import { cn } from "@/utils/cn";

import PropTypes from "prop-types";

export const Sidebar = forwardRef(({ collapsed }, ref) => {
    return (
        <aside
            ref={ref}
            className={cn(
                "fixed z-[100] flex h-full w-[240px] flex-col overflow-x-hidden border-r border-slate-300 bg-white transition-all duration-300 ease-in-out dark:border-slate-700 dark:bg-slate-900",
                collapsed ? "md:w-[70px]" : "md:w-[240px]",
                collapsed ? "max-md:-left-full" : "max-md:left-0"
            )}
        >
            <Link 
                to="/"
                className="flex h-16 items-center gap-x-3 border-b border-slate-300 px-4 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            >
                <div className="flex h-10 w-10 items-center justify-center">
                    <img
                        src={logoLight}
                        alt="GTRON"
                        className="h-full w-full object-contain dark:hidden"
                    />
                    <img
                        src={logoDark}
                        alt="GTRON"
                        className="hidden h-full w-full object-contain dark:block"
                    />
                </div>
                {!collapsed && (
                    <p className="text-lg font-medium text-slate-900 transition-colors dark:text-slate-50">
                        G-TRON
                    </p>
                )}
            </Link>
            <div className="flex flex-1 flex-col gap-y-6 overflow-y-auto p-4 [scrollbar-width:_thin]">
                {navbarLinks.map((navbarLink) => (
                    <nav
                        key={navbarLink.title}
                        className={cn(
                            "flex flex-col gap-y-1",
                            collapsed && "md:items-center"
                        )}
                    >
                        <p className={cn(
                            "mb-2 text-sm font-medium text-slate-600 dark:text-slate-400",
                            collapsed && "md:w-[45px] md:text-center"
                        )}>
                            {navbarLink.title}
                        </p>
                        
                        {navbarLink.links.map((link) => (
                            <NavLink
                                key={link.label}
                                to={link.path}
                                className={({ isActive }) => cn(
                                    "flex h-10 items-center gap-x-3 rounded-lg px-3 text-base font-medium text-slate-900 transition-all duration-200 ease-in-out hover:bg-sky-400 hover:text-white dark:text-slate-50 dark:hover:bg-sky-500",
                                    isActive && "bg-sky-400 text-white dark:bg-sky-500",
                                    collapsed && "md:justify-center md:px-2"
                                )}
                            >
                                <link.icon
                                    size={22}
                                    className="flex-shrink-0"
                                />
                                {!collapsed && (
                                    <span className="truncate">
                                        {link.label}
                                    </span>
                                )}
                            </NavLink>
                        ))}
                    </nav>
                ))}
            </div>
        </aside>
    );
});

Sidebar.displayName = "Sidebar";

Sidebar.propTypes = {
    collapsed: PropTypes.bool,
};
