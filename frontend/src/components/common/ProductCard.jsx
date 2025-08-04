import styled from 'styled-components';

const ProductCard = ({ image, name, price }) => (
  <Card>
    <Img src={image} alt={name} />
    <Name>{name}</Name>
    <Price>{price}원</Price>
  </Card>
);

const Card = styled.div`
  background: #fff;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 1.2rem 1rem 1.5rem 1rem;
  text-align: center;
  transition: box-shadow 0.2s;
  &:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.07);
  }
`;
const Img = styled.img`
  width: 100%;
  height: 220px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 1rem;
`;
const Name = styled.div`
  font-weight: 700;
  margin-bottom: 0.5rem;
`;
const Price = styled.div`
  color: #888;
  font-size: 1rem;
`;

export default ProductCard;