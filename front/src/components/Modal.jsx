import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import './Modal.css';

const Modal = ({ isOpen, onClose, title, children, width = 420 }) => {
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') onClose?.();
    };
    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return createPortal(
    (
      <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
        <div
          className="modal-container"
          style={{ width }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="modal-header">
            {title && <h3 className="modal-title">{title}</h3>}
            <button className="modal-close" onClick={onClose} aria-label="Close">
              ×
            </button>
          </div>
          <div className="modal-content">{children}</div>
        </div>
      </div>
    ),
    document.body
  );
};

export default Modal;


