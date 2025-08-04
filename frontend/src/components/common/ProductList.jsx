import React from 'react';
import styled from 'styled-components';

const ProductList = ({ title, count, items }) => {
  return (
    <Section>
      <Title>
        {title}
        {count && <Count>({count})</Count>}
      </Title>
      <List>
        {items.map(item => (
          <Product key={item.id}>
            <Image src={item.imageUrl} alt={item.name} />
            <Name>{item.name}</Name>
            <Price>{item.price}원</Price>
          </Product>
        ))}
      </List>
    </Section>
  );
};

export default ProductList;

const Section = styled.section`
  margin: 3rem 0 2rem 0;
`;

const Title = styled.h2`
  font-size: 1.5rem;
  font-weight: 900;
  margin-bottom: 1.2rem;
  letter-spacing: -1px;
`;

const Count = styled.span`
  color: #1a4cff;
  font-size: 1rem;
  margin-left: 0.5rem;
`;

const List = styled.div`
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
`;

const Product = styled.div`
  flex: 1 1 200px;
  min-width: 200px;
  max-width: 240px;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  text-align: center;
`;

const Image = styled.img`
  width: 100%;
  height: 180px;
  object-fit: cover;
`;

const Name = styled.div`
  font-weight: bold;
  margin: 0.7rem 0 0.3rem 0;
`;

const Price = styled.div`
  color: #666;
  margin-bottom: 1rem;
`;