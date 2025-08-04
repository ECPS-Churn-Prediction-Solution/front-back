import styled from 'styled-components';

const SectionTitle = ({ children, right }) => (
  <TitleBox>
    <span>{children}</span>
    {right && <Right>{right}</Right>}
  </TitleBox>
);

const TitleBox = styled.div`
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 2rem;
  span {
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1;
  }
`;
const Right = styled.div`
  font-size: 1rem;
  color: #888;
`;

export default SectionTitle;