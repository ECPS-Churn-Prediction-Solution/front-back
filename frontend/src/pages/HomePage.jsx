import React from 'react';
import styled from 'styled-components';

const HomePage = () => (
  <MainWrapper>
    <Header>
      <Nav>
        <NavItem>Home</NavItem>
        <NavItem>Collections</NavItem>
        <NavItem>New</NavItem>
      </Nav>
      <Icons>
        <Circle />
        <Circle />
        <Circle />
        <CartBtn>Cart</CartBtn>
      </Icons>
    </Header>
    <SideCategory>
      <Cat>MEN</Cat>
      <Cat>WOMEN</Cat>
      <Cat>KIDS</Cat>
    </SideCategory>
    <MainTitle>
      <Title>NEW<br />COLLECTION</Title>
      <SubTitle>Summer <br />2024</SubTitle>
    </MainTitle>
    <ProductRow>
      <ProductCard />
      <ProductCard />
    </ProductRow>
    <GoShopRow>
      <GoShopBtn>Go To Shop</GoShopBtn>
      <NavBtn>{'<'}</NavBtn>
      <NavBtn>{'>'}</NavBtn>
    </GoShopRow>
    {/* 이하 신상, 카테고리, 소개, 룩북, 푸터 등 추가 가능 */}
  </MainWrapper>
);

const MainWrapper = styled.div`
  background: #f5f5f5;
  min-height: 100vh;
  padding: 0 50px;
  font-family: 'Inter', 'Noto Sans KR', sans-serif;
`;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40px 0 0 0;
`;

const Nav = styled.nav`
  display: flex;
  gap: 40px;
`;

const NavItem = styled.div`
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 2px;
`;

const Icons = styled.div`
  display: flex;
  align-items: center;
  gap: 24px;
`;

const Circle = styled.div`
  width: 50px; height: 50px; background: #000; border-radius: 50%;
`;

const CartBtn = styled.div`
  background: #000; color: #fff; border-radius: 22px; padding: 12px 24px;
  font-size: 12px; font-weight: 500; letter-spacing: 2px;
`;

const SideCategory = styled.div`
  position: absolute; left: 50px; top: 156px;
  display: flex; flex-direction: column; gap: 8px;
`;

const Cat = styled.div`
  font-size: 16px; font-weight: 400; letter-spacing: 2px;
`;

const MainTitle = styled.div`
  position: absolute; left: 50px; top: 386px;
`;

const Title = styled.div`
  font-size: 48px; font-weight: 800; text-transform: uppercase; line-height: 40px; letter-spacing: 2px;
`;

const SubTitle = styled.div`
  font-size: 16px; font-weight: 400; letter-spacing: 2px; margin-top: 24px;
`;

const ProductRow = styled.div`
  display: flex; gap: 40px; margin-top: 200px;
`;

const ProductCard = () => (
  <Card>
    <img src="https://placehold.co/366x376" alt="product" style={{width: '100%', borderRadius: 8}} />
    <CardTitle>Basic Heavy Weight T-shirt</CardTitle>
    <CardPrice>$199</CardPrice>
  </Card>
);

const Card = styled.div`
  width: 366px; height: 376px; border: 1px #D7D7D7 solid; background: #fff; border-radius: 8px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
`;

const CardTitle = styled.div`
  font-size: 14px; font-weight: 500; margin-top: 16px;
`;

const CardPrice = styled.div`
  font-size: 16px; font-weight: 500; margin-top: 8px;
`;

const GoShopRow = styled.div`
  display: flex; align-items: center; gap: 16px; margin-top: 32px;
`;

const GoShopBtn = styled.button`
  background: #D9D9D9; border-radius: 2px; border: none; padding: 12px 32px;
  font-size: 16px; font-weight: 500; margin-right: 16px;
`;

const NavBtn = styled.button`
  width: 40px; height: 40px; border: 1px #A3A3A3 solid; background: none; border-radius: 50%;
  font-size: 20px; color: #222; display: flex; align-items: center; justify-content: center;
`;

export default HomePage;
