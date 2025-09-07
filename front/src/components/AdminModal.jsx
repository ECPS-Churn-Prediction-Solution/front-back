import React, { useState, useEffect } from "react";
import "./AdminModal.css";

const AdminModal = ({ isOpen, onClose, onSave, admin }) => {
  const isEditMode = Boolean(admin);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
    phoneNumber: "",
  });

  useEffect(() => {
    if (isOpen) {
      if (isEditMode) {
        setFormData({
          email: admin.email || "",
          password: "",
          name: admin.name || "",
          phoneNumber: admin.phoneNumber || "",
        });
      } else {
        setFormData({
          email: "",
          password: "",
          name: "",
          phoneNumber: "",
        });
      }
    }
  }, [isOpen, admin, isEditMode]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email) {
      alert("이름과 이메일은 필수 항목입니다.");
      return;
    }
    if (!isEditMode && !formData.password) {
      alert("새 관리자 등록 시 비밀번호는 필수입니다.");
      return;
    }
    onSave(formData);
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2>관리자 {isEditMode ? "수정" : "등록"}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">이메일</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">비밀번호</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder={isEditMode ? "변경할 경우에만 입력" : ""}
              required={!isEditMode}
            />
          </div>
          <div className="form-group">
            <label htmlFor="name">이름</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="phoneNumber">전화번호</label>
            <input
              type="tel"
              id="phoneNumber"
              name="phoneNumber"
              value={formData.phoneNumber}
              onChange={handleChange}
            />
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-cancel" onClick={onClose}>
              취소
            </button>
            <button type="submit" className="btn-save">
              저장
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AdminModal;
