import React from 'react';

const AddProductModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
   <div className="fixed inset-0 backdrop-blur-sm bg-black/10 z-50 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg w-1/3 shadow-xl">
        <h2 className="text-xl font-semibold mb-4">Add Product</h2>
        {/* Form content here */}
        <button className="mt-4 px-4 py-2 bg-gray-900 text-white rounded" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
};

export default AddProductModal;
