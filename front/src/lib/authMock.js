// 간단한 로컬스토리지 기반 더미 인증 모듈
// 데이터 스키마는 백엔드 응답(UserResponse) 형태를 최대한 맞춥니다.

const STORAGE_USERS = 'mockUsers';
const STORAGE_CURRENT_USER_ID = 'mockCurrentUserId';

function loadUsers() {
  const raw = localStorage.getItem(STORAGE_USERS);
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

function saveUsers(users) {
  localStorage.setItem(STORAGE_USERS, JSON.stringify(users));
}

function getNextUserId(users) {
  const max = users.reduce((acc, u) => Math.max(acc, u.user_id || 0), 0);
  return max + 1;
}

function stripSensitive(user) {
  if (!user) return null;
  const { password, ...safe } = user;
  return safe;
}

export function getMe() {
  const id = Number(localStorage.getItem(STORAGE_CURRENT_USER_ID) || 0);
  if (!id) return null;
  const users = loadUsers();
  const found = users.find((u) => u.user_id === id);
  return stripSensitive(found);
}

export function logout() {
  localStorage.removeItem(STORAGE_CURRENT_USER_ID);
}

export function login({ email, password }) {
  const users = loadUsers();
  const found = users.find((u) => u.email === email && u.password === password);
  if (!found) throw new Error('이메일 또는 비밀번호가 올바르지 않습니다.');
  localStorage.setItem(STORAGE_CURRENT_USER_ID, String(found.user_id));
  return stripSensitive(found);
}

export function register({ email, password, user_name, gender = 'other', birthdate, phone_number, interest_categories = [] }) {
  if (!email || !password || !user_name || !birthdate) {
    throw new Error('필수 항목이 누락되었습니다.');
  }
  if (password.length < 6) {
    throw new Error('비밀번호는 6자 이상이어야 합니다.');
  }
  const users = loadUsers();
  if (users.some((u) => u.email === email)) {
    throw new Error('이미 존재하는 이메일입니다.');
  }
  const now = new Date().toISOString();
  const newUser = {
    user_id: getNextUserId(users),
    email,
    user_name,
    gender,
    birthdate,
    phone_number: phone_number || null,
    created_at: now,
    interest_categories,
    // 더미에서는 평문 저장 (실서비스에서는 해싱 필요)
    password,
  };
  users.push(newUser);
  saveUsers(users);
  return stripSensitive(newUser);
}


