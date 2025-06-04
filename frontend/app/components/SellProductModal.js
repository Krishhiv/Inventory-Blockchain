'use client';

import React, { useState } from 'react';

const SellProductModal = ({ isOpen, onClose }) => {
  const [productId, setProductId] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');

  const handleSell = () => {
    // Placeholder: Add logic to call backend for selling a product
    console.log('Selling product:', productId, 'to:', customerEmail);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 backdrop-blur-sm bg-black/10 z-50 flex items-center justify-center">
      <div className="bg-black p-6 rounded-xl w-1/3 shadow-xl">
        <h2 className="text-xl font-semibold mb-4">Sell Product</h2>

        <input
          type="text"
          placeholder="Product ID"
          className="w-full mb-3 p-2 border rounded"
          value={productId}
          onChange={(e) => setProductId(e.target.value)}
        />

        <input
          type="email"
          placeholder="Customer Email"
          className="w-full mb-4 p-2 border rounded"
          value={customerEmail}
          onChange={(e) => setCustomerEmail(e.target.value)}
        />

        <div className="flex justify-end space-x-3">
          <button onClick={onClose} className="px-4 text-black font-bold py-2 bg-gray-200 rounded">
            Cancel
          </button>
          <button onClick={handleSell} className="px-4 py-2 bg-green-600 text-white font-bold rounded">
            Confirm Sale
          </button>
        </div>
      </div>
    </div>
  );
};

export default SellProductModal;
