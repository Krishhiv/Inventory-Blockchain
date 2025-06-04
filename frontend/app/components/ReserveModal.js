'use client';

import React, { useState } from 'react';

const ReserveModal = ({ isOpen, onClose }) => {
  const [productId, setProductId] = useState('');
  const [reservationUntil, setReservationUntil] = useState('');

  const handleReserve = () => {
    // Placeholder: Add logic to reserve the product in backend
    console.log('Reserving product:', productId, 'until:', reservationUntil);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 backdrop-blur-sm bg-black/10 z-50 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg w-1/3 shadow-xl">
        <h2 className="text-xl font-semibold mb-4">Reserve Product</h2>

        <input
          type="text"
          placeholder="Product ID"
          className="w-full mb-3 p-2 border rounded"
          value={productId}
          onChange={(e) => setProductId(e.target.value)}
        />

        <input
          type="datetime-local"
          className="w-full mb-4 p-2 border rounded"
          value={reservationUntil}
          onChange={(e) => setReservationUntil(e.target.value)}
        />

        <div className="flex justify-end space-x-3">
          <button onClick={onClose} className="px-4 py-2 bg-gray-200 rounded">
            Cancel
          </button>
          <button onClick={handleReserve} className="px-4 py-2 bg-blue-600 text-white rounded">
            Confirm Reservation
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReserveModal;
