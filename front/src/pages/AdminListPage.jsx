import React, { useState, useEffect } from "react";
import AdminModal from "../components/AdminModal";
import "./AdminListPage.css";

const initialAdmins = [
  {
    id: 1,
    email: "admin@example.com",
    name: "김관리",
    phoneNumber: "010-1234-5678",
  },
  {
    id: 2,
    email: "super@example.com",
    name: "박슈퍼",
    phoneNumber: "010-1111-2222",
  },
];

const AdminListPage = () => {
  const [admins, setAdmins] = useState(initialAdmins);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [selectedAdmin, setSelectedAdmin] = useState(null);

  const handleOpenModal = (admin = null) => {
    setSelectedAdmin(admin);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setSelectedAdmin(null);
    setIsModalOpen(false);
  };

  const handleSaveAdmin = (adminData) => {
    if (selectedAdmin) {
      setAdmins(
        admins.map((admin) =>
          admin.id === selectedAdmin.id
            ? {
                ...admin,
                ...adminData,
                password: adminData.password
                  ? adminData.password
                  : admin.password,
              }
            : admin
        )
      );
      alert("관리자 정보가 수정되었습니다.");
    } else {
      const newAdmin = {
        id: Date.now(),
        ...adminData,
      };
      setAdmins([...admins, newAdmin]);
      alert("새로운 관리자가 등록되었습니다.");
    }
    handleCloseModal();
  };

  const handleDeleteAdmin = (adminId) => {
    if (window.confirm("정말로 이 관리자를 삭제하시겠습니까?")) {
      setAdmins(admins.filter((admin) => admin.id !== adminId));
      alert("관리자가 삭제되었습니다.");
    }
  };

  return (
    <div className="admin-list-container">
      <div className="admin-list-header">
        <h1>관리자 목록</h1>
        <button className="add-admin-btn" onClick={() => handleOpenModal()}>
          + 관리자 등록
        </button>
      </div>

      <table className="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>이메일</th>
            <th>이름</th>
            <th>전화번호</th>
            <th>관리</th>
          </tr>
        </thead>
        <tbody>
          {admins.map((admin) => (
            <tr key={admin.id}>
              <td>{admin.id}</td>
              <td>{admin.email}</td>
              <td>{admin.name}</td>
              <td>{admin.phoneNumber}</td>
              <td>
                <button
                  className="btn-edit"
                  onClick={() => handleOpenModal(admin)}
                >
                  수정
                </button>
                <button
                  className="btn-delete"
                  onClick={() => handleDeleteAdmin(admin.id)}
                >
                  삭제
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <AdminModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSave={handleSaveAdmin}
        admin={selectedAdmin}
      />
    </div>
  );
};

export default AdminListPage;
