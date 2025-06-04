'use client';

import React from 'react';

const NavBar = ({ onOpenAdd, onOpenSell, onOpenReserve }) => {
  return (
    <div className="h-screen w-64 pt-10 bg-gray-900 text-white p-4 flex flex-col space-y-6">
      
      {/* Main */}
      <div className="space-y-2">
        <button className="w-full text-left px-4 py-2 rounded-lg hover:bg-gray-800" onClick={() => window.location.reload()}>
          Dashboard
        </button>
        <button className="w-full text-left px-4 py-2 rounded-lg hover:bg-gray-800" onClick={onOpenAdd}>
          Add Product
        </button>
        <button className="w-full text-left px-4 py-2 rounded-lg hover:bg-gray-800" onClick={onOpenSell}>
          Sell Product
        </button>
        <button className="w-full text-left px-4 py-2 rounded-lg hover:bg-gray-800" onClick={onOpenReserve}>
          Reserve Item
        </button>
      </div>

      {/* Other buttons can be hooked later */}
      <button className="w-full text-left bg-red-400 px-4 py-2 mt-auto rounded-lg font-bold hover:bg-red-600" 
        onClick={() => {
            // Clear stored auth data
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user_email'); // if you store this

            // Redirect to login
            window.location.href = '/login'; // or use router.push if using useRouter()
        }}>
          Logout
        </button>
    </div>
  );
};

export default NavBar;
