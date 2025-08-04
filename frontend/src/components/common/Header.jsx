import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { FiMenu, FiSearch, FiUser, FiShoppingCart, FiSun } from 'react-icons/fi';

const Header = () => {
  return (
    <HeaderContainer>
      <TopSection>
        <HamburgerMenu>
          <FiMenu />
        </HamburgerMenu>
        <Nav>
          <NavLink to="/">Home</NavLink>
          <NavLink to="/category/men">Men</NavLink>
          <NavLink to="/category/women">Women</NavLink>
          <NavLink to="/category/kids">Kids</NavLink>
          <NavLink to="/admin">Admin</NavLink>
        </Nav>
        <Logo>
          <Link to="/">YourLogo</Link>
        </Logo>
        <Icons>
          <IconButton><FiSun /></IconButton>
          <IconButton><Link to="/cart"><FiShoppingCart /></Link></IconButton>
          <IconButton><FiUser /></IconButton>
        </Icons>
      </TopSection>
      <BottomSection>
        <CategoryNav>
          <CategoryLink to="/category/men">MEN</CategoryLink>
          <CategoryLink to="/category/women">WOMEN</CategoryLink>
          <CategoryLink to="/category/kids">KIDS</CategoryLink>
        </CategoryNav>
        <SearchBar>
          <FiSearch />
          <SearchInput type="text" placeholder="Search" />
        </SearchBar>
      </BottomSection>
    </HeaderContainer>
  );
};

export default Header;

const HeaderContainer = styled.header`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: #fff;
  border-bottom: 1px solid #eee;
  padding: 1rem 2rem;
  z-index: 1000;
`;

const TopSection = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const BottomSection = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
`;

const Nav = styled.nav`
  display: flex;
  gap: 2rem;
  @media (max-width: 768px) {
    display: none;
  }
`;

const NavLink = styled(Link)`
  font-weight: 700;
  color: #333;
  &:hover {
    color: #000;
  }
`;

const Logo = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
`;

const Icons = styled.div`
  display: flex;
  align-items: center;
  gap: 1.5rem;
`;

const IconButton = styled.button`
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const HamburgerMenu = styled.div`
  display: none;
  font-size: 1.5rem;
  @media (max-width: 768px) {
    display: block;
  }
`;

const CategoryNav = styled.div`
  display: flex;
  gap: 1.5rem;
`;

const CategoryLink = styled(Link)`
  font-size: 0.9rem;
  font-weight: bold;
  color: #555;
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  background-color: #f5f5f5;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  width: 250px;
`;

const SearchInput = styled.input`
  border: none;
  background: transparent;
  outline: none;
  margin-left: 0.5rem;
  width: 100%;
`;
