'use client';

import React, { useEffect, useState } from 'react';
import AddProductModal from '../components/AddProductModal';
import SellProductModal from '../components/SellProductModal';
import ReserveModal from '../components/ReserveModal';
import CreateCustomerModal from '../components/CreateCustomerModal';
import { useRouter } from 'next/navigation';

const DashboardPage = () => {
  const [inventory, setInventory] = useState([]);
  const [isAddOpen, setAddOpen] = useState(false);
  const [isSellOpen, setSellOpen] = useState(false);
  const [isReserveOpen, setReserveOpen] = useState(false);
  const [isCustomerModalOpen, setCustomerModalOpen] = useState(false);

  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  useEffect(() => {
    const testData = {
      A: {
        uid: 1,
        brand: 'Louis Vuitton',
        item_name: 'Handbag',
        price: 150000,
        status: 'available',
        timestamp: '2025-06-04 10:00',
        next: {
          uid: 2,
          brand: 'Louis Vuitton',
          item_name: 'Wallet',
          price: 60000,
          status: 'sold',
          timestamp: '2025-06-03 14:23',
          next: null,
        },
      },
      B: {
        uid: 3,
        brand: 'Rolex',
        item_name: 'Watch',
        price: 550000,
        status: 'available',
        timestamp: '2025-06-02 16:45',
        next: null,
      },
    };

    const flattenBlockchain = (chains) => {
      const items = [];
      for (const key in chains) {
        let block = chains[key];
        while (block) {
          if (block.uid !== 0 && !block.brand.toLowerCase().includes('genesis')) {
            items.push(block);
          }
          block = block.next;
        }
      }
      return items;
    };

    const flattened = flattenBlockchain(testData);
    setInventory(flattened);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Top Row: Title, Add Button, and Logout */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-black">Inventory</h1>
          <button
            onClick={() => setAddOpen(true)}
            className="px-4 py-2 text-sm font-medium bg-green-600 text-white rounded hover:bg-green-700"
          >
            + Add Inventory
          </button>
          <button
            onClick={() => setCustomerModalOpen(true)}
            className="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            + Create Customer Account
          </button>
        </div>
        <button
          onClick={handleLogout}
          className="px-4 py-2 text-sm font-medium bg-red-600 text-white rounded hover:bg-red-700"
        >
          Logout
        </button>
      </div>



      {/* Table */}
      <div className="overflow-auto max-h-[500px] border rounded-lg shadow">
        <table className="min-w-full text-left border-collapse">
          <thead className="bg-gray-200 sticky top-0 z-10">
            <tr>
              <th className="p-3 text-sm font-semibold text-gray-700 border-b">UID</th>
              <th className="p-3 text-sm font-semibold text-gray-700 border-b">Brand</th>
              <th className="p-3 text-sm font-semibold text-gray-700 border-b">Item</th>
              <th className="p-3 text-sm font-semibold text-gray-700 border-b">Price</th>
              <th className="p-3 text-sm font-semibold text-gray-700 border-b">Status</th>
              <th className="p-3 text-sm font-semibold text-gray-700 border-b">Date</th>
              <th className="p-3 text-sm font-semibold text-gray-700 border-b">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {inventory.map((item, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="p-3 text-sm text-gray-800">{item.uid}</td>
                <td className="p-3 text-sm text-gray-800">{item.brand}</td>
                <td className="p-3 text-sm text-gray-800">{item.item_name}</td>
                <td className="p-3 text-sm text-gray-800">₹{item.price.toLocaleString()}</td>
                <td className="p-3 text-sm text-gray-800">{item.status}</td>
                <td className="p-3 text-sm text-gray-800">{item.timestamp}</td>
                <td className="p-3 text-sm text-gray-800">
                  <button onClick={() => setSellOpen(true)} className="text-blue-600 hover:cursor-pointer hover:underline mr-2">Sell</button>
                  <button onClick={() => setReserveOpen(true)} className="text-yellow-600 hover:cursor-pointer hover:underline">Reserve</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modals */}
      <AddProductModal isOpen={isAddOpen} onClose={() => setAddOpen(false)} />
      <SellProductModal isOpen={isSellOpen} onClose={() => setSellOpen(false)} />
      <ReserveModal isOpen={isReserveOpen} onClose={() => setReserveOpen(false)} />
        <CreateCustomerModal isOpen={isCustomerModalOpen} onClose={() => setCustomerModalOpen(false)}/>

    </div>
  );
};

export default DashboardPage;
