import React from 'react';
import styled from 'styled-components';
import SectionTitle from '../common/SectionTitle';
import MinimalButton from '../common/MinimalButton';
import ProductCard from '../common/ProductCard';

const NewCollectionSection = ({ collection }) => {
  return (
    <Section>
      <SectionTitle>{collection.title}<Sub>{collection.season}</Sub></SectionTitle>
      <Row>
        {collection.items.map(item => (
          <ProductCard key={item.id} image={item.imageUrl} name={item.name} price={item.price} />
        ))}
      </Row>
      <ButtonRow>
        <MinimalButton>Go To Shop</MinimalButton>
        <NavBtns>
          <CircleBtn>{'<'}</CircleBtn>
          <CircleBtn>{'>'}</CircleBtn>
        </NavBtns>
      </ButtonRow>
    </Section>
  );
};

const Section = styled.section`
  margin: 4rem 0 3rem 0;
`;
const Sub = styled.span`
  display: block;
  font-size: 1rem;
  color: #888;
  font-weight: 400;
  margin-top: 0.5rem;
`;
const Row = styled.div`
  display: flex;
  gap: 2.5rem;
  margin-bottom: 2rem;
`;
const ButtonRow = styled.div`
  display: flex;
  align-items: center;
  gap: 1.5rem;
`;
const NavBtns = styled.div`
  display: flex;
  gap: 0.5rem;
`;
const CircleBtn = styled.button`
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid #ccc;
  background: #fff;
  color: #222;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  &:hover {
    background: #eee;
  }
`;

export default NewCollectionSection;