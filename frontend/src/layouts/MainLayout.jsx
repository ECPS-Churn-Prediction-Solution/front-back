import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from '../components/common/Header';
import Footer from '../components/common/Footer';
import styled from 'styled-components';

const MainLayout = () => (
  <Wrapper>
    <Header />
    <Main>
      <Outlet />
    </Main>
    <Footer />
  </Wrapper>
);

const Wrapper = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;
const Main = styled.main`
  flex: 1;
  width: 100%;
`;

export default MainLayout;
