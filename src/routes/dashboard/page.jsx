import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { useTheme } from "@/hooks/use-theme";

import { overviewData, recentTransactionsData   , topEwasteItems } from "@/constants";

import { Footer } from "@/layouts/footer";

import { CreditCard, DollarSign, Package, PencilLine, Star, Trash, TrendingUp, Users } from "lucide-react";
import {   Recycle, AlertTriangle } from "lucide-react";



const DashboardPage = () => {
    const { theme } = useTheme();

    return (
        <div className="flex flex-col gap-y-4">
            <h1 className="title">Dashboard</h1>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
    {/* Total E-Waste Collected */}
    <div className="card">
        <div className="card-header">
            <div className="w-fit rounded-lg bg-green-500/20 p-2 text-green-500 transition-colors dark:bg-green-600/20 dark:text-green-600">
                <Package size={26} />
            </div>
            <p className="card-title">Total E-Waste Collected</p>
        </div>
        <div className="card-body bg-slate-100 transition-colors dark:bg-slate-950">
            <p className="text-3xl font-bold text-slate-900 transition-colors dark:text-slate-50">50,000 kg</p>
            <span className="flex w-fit items-center gap-x-2 rounded-full border border-green-500 px-2 py-1 font-medium text-green-500 dark:border-green-600 dark:text-green-600">
                <TrendingUp size={18} />
                30% Increase
            </span>
        </div>
    </div>

    {/* Total Hazardous Waste Identified */}
    <div className="card">
        <div className="card-header">
            <div className="rounded-lg bg-red-500/20 p-2 text-red-500 transition-colors dark:bg-red-600/20 dark:text-red-600">
                <AlertTriangle size={26} />
            </div>
            <p className="card-title">Hazardous Waste Identified</p>
        </div>
        <div className="card-body bg-slate-100 transition-colors dark:bg-slate-950">
            <p className="text-3xl font-bold text-slate-900 transition-colors dark:text-slate-50">12,000 kg</p>
            <span className="flex w-fit items-center gap-x-2 rounded-full border border-red-500 px-2 py-1 font-medium text-red-500 dark:border-red-600 dark:text-red-600">
                <TrendingUp size={18} />
                18% Increase
            </span>
        </div>
    </div>

    {/* Total E-Waste Recycled */}
    <div className="card">
        <div className="card-header">
            <div className="rounded-lg bg-blue-500/20 p-2 text-blue-500 transition-colors dark:bg-blue-600/20 dark:text-blue-600">
                <Recycle size={26} />
            </div>
            <p className="card-title">Total E-Waste Recycled</p>
        </div>
        <div className="card-body bg-slate-100 transition-colors dark:bg-slate-950">
            <p className="text-3xl font-bold text-slate-900 transition-colors dark:text-slate-50">35,500 kg</p>
            <span className="flex w-fit items-center gap-x-2 rounded-full border border-blue-500 px-2 py-1 font-medium text-blue-500 dark:border-blue-600 dark:text-blue-600">
                <TrendingUp size={18} />
                25% Efficiency
            </span>
        </div>
    </div>

    {/* Total Revenue Generated from Recycling */}
    <div className="card">
        <div className="card-header">
            <div className="rounded-lg bg-yellow-500/20 p-2 text-yellow-500 transition-colors dark:bg-yellow-600/20 dark:text-yellow-600">
                <DollarSign size={26} />
            </div>
            <p className="card-title">Revenue from Recycling</p>
        </div>
        <div className="card-body bg-slate-100 transition-colors dark:bg-slate-950">
            <p className="text-3xl font-bold text-slate-900 transition-colors dark:text-slate-50">₹1,25,000</p>
            <span className="flex w-fit items-center gap-x-2 rounded-full border border-yellow-500 px-2 py-1 font-medium text-yellow-500 dark:border-yellow-600 dark:text-yellow-600">
                <TrendingUp size={18} />
                22% Growth
            </span>
        </div>
    </div>
</div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-7">
                <div className="card col-span-1 md:col-span-2 lg:col-span-4">
                    <div className="card-header">
                     <p className="card-title">E-Waste Processing Overview</p>
</div>
<div className="card-body p-0">
    <ResponsiveContainer width="100%" height={300}>
        <AreaChart
            data={overviewData}
            margin={{
                top: 0,
                right: 0,
                left: 0,
                bottom: 0,
            }}
        >
            <defs>
                <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.8} />  
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
            </defs>
            <Tooltip cursor={false} formatter={(value) => `${value} Tons`} />

            <XAxis
                dataKey="name"
                strokeWidth={0}
                stroke={theme === "light" ? "#475569" : "#94a3b8"}
                tickMargin={6}
            />
            <YAxis
                dataKey="total"
                strokeWidth={0}
                stroke={theme === "light" ? "#475569" : "#94a3b8"}
                tickFormatter={(value) => `${value} Tons`}
                tickMargin={6}
            />

            <Area
                type="monotone"
                dataKey="total"
                stroke="#22c55e" 
                fillOpacity={1}
                fill="url(#colorTotal)"
            />
        </AreaChart>
    </ResponsiveContainer>
</div>

                </div>
                <div className="card col-span-1 md:col-span-2 lg:col-span-3">
    <div className="card-header">
        <p className="card-title">Recent E-Waste Transactions</p>
    </div>
    <div className="card-body h-[300px] overflow-auto p-0">
        {recentTransactionsData.map((transaction) => (
            <div
                key={transaction.id}
                className="flex items-center justify-between gap-x-4 py-2 pr-2"
            >
                <div className="flex items-center gap-x-4">
                    <img
                        src={transaction.image}
                        alt={transaction.name}
                        className="size-10 flex-shrink-0 rounded-full object-cover"
                    />
                    <div className="flex flex-col gap-y-2">
                        <p className="font-medium text-slate-900 dark:text-slate-50">
                            {transaction.name}
                        </p>
                        <p className="text-sm text-slate-600 dark:text-slate-400">
                            {transaction.email}
                        </p>
                    </div>
                </div>
                <p className="font-medium text-green-600 dark:text-green-400">
                    {transaction.total} kg
                </p>
            </div>
        ))}
    </div>
</div>

            </div>
            <div className="card">
            <div className="card-header">
        <p className="card-title">Top E-Waste Items</p>
    </div>
                <div className="card-body p-0">
                    <div className="relative h-[500px] w-full flex-shrink-0 overflow-auto rounded-none [scrollbar-width:_thin]">
                        <table className="table">
                            <thead className="table-header">
                                <tr className="table-row">
                                    <th className="table-head">#</th>
                                    <th className="table-head">Product</th>
                                    <th className="table-head">Price</th>
                                    <th className="table-head">Status</th>
                                    <th className="table-head">Rating</th>
                                    <th className="table-head">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="table-body">
                                {topEwasteItems.map((product) => (
                                    <tr
                                        key={product.number}
                                        className="table-row"
                                    >
                                        <td className="table-cell">{product.number}</td>
                                        <td className="table-cell">
                                            <div className="flex w-max gap-x-4">
                                                <img
                                                    src={product.image}
                                                    alt={product.name}
                                                    className="size-14 rounded-lg object-cover"
                                                />
                                                <div className="flex flex-col">
                                                    <p>{product.name}</p>
                                                    <p className="font-normal text-slate-600 dark:text-slate-400">{product.description}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="table-cell">${product.price}</td>
                                        <td className="table-cell">{product.status}</td>
                                        <td className="table-cell">
                                            <div className="flex items-center gap-x-2">
                                                <Star
                                                    size={18}
                                                    className="fill-yellow-600 stroke-yellow-600"
                                                />
                                                {product.rating}
                                            </div>
                                        </td>
                                        <td className="table-cell">
                                            <div className="flex items-center gap-x-4">
                                                <button className="text-blue-500 dark:text-blue-600">
                                                    <PencilLine size={20} />
                                                </button>
                                                <button className="text-red-500">
                                                    <Trash size={20} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <Footer />
        </div>
    );
};

export default DashboardPage;
