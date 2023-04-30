from unittest.mock import Mock, patch
from datetime import datetime
from hotel_business_module.tests.base_test import BaseTest
from hotel_business_module.gateways.categories_gateway import CategoriesGateway
from hotel_business_module.gateways.tags_gateway import TagsGateway
from hotel_business_module.models.categories import Category
from hotel_business_module.models.tags import Tag
from hotel_business_module.tests.session import get_session


class TestCategories(BaseTest):
    @patch('hotel_business_module.utils.file_manager.FileManager.save_file')
    def test_save(self, mock_save_file: Mock):
        """
        Тестирования сохранения категории
        """
        # мокаем метод сохранения файла, чтоб реально не сохранять, а просто получить имя
        mock_save_file.return_value = 'C:\\images\\image1.jpg'
        # мокаем файл, чтоб отправить его как параметр
        file = Mock()
        with get_session() as session:
            # создаем категории
            category = Category(
                name='test_category',
                description='lorem ipsum...',
                price=999,
                prepayment_percent=10,
                refund_percent=50,
                rooms_count=2,
                floors=1,
                beds=2,
                square=50
            )
            CategoriesGateway.save_category(category, session, file=file, file_name=file.name)

            # проверяем, что сохранилось
            self.assertIsNotNone(CategoriesGateway.get_by_id(category.id, session))
            # проверяем, присвоился ли путь
            self.assertEqual(category.main_photo_path, 'C:\\images\\image1.jpg')

            category.name = 'test_category_edited'
            CategoriesGateway.save_category(category, session)
            # проверяем не сломается ли путь при изменение сторонних свойств
            self.assertEqual(category.main_photo_path, 'C:\\images\\image1.jpg')

    @patch('hotel_business_module.utils.file_manager.FileManager.save_file')
    def test_delete(self, mock_save_file: Mock):
        """
        Тестирование удаления
        """
        mock_save_file.return_value = 'C:\\images\\image1.jpg'
        file = Mock()
        with get_session() as session:
            category = Category(
                name='test_category',
                description='lorem ipsum...',
                price=999,
                prepayment_percent=10,
                refund_percent=50,
                rooms_count=2,
                floors=1,
                beds=2,
                square=50
            )
            # сохранеяем категорию
            CategoriesGateway.save_category(category, session, file=file, file_name=file.name)

            category_id = category.id
            # удаляем
            CategoriesGateway.delete_category(category, session)
            # проверяем, удалилась ли
            self.assertIsNone(CategoriesGateway.get_by_id(category_id, session))

    @patch('hotel_business_module.utils.file_manager.FileManager.save_file')
    def test_get(self,  mock_save_file: Mock):
        """
        Тестирвоание получения списка активных категорий
        """
        mock_save_file.return_value = 'C:\\images\\image1.jpg'
        file = Mock()
        with get_session() as session:
            # создаем активную категорию
            category = Category(
                name='test_category',
                description='lorem ipsum...',
                price=999,
                prepayment_percent=10,
                refund_percent=50,
                rooms_count=2,
                floors=1,
                beds=2,
                square=50
            )
            # создаем удаленную категорию
            deleted_category = Category(
                name='deleted_test_category',
                description='lorem ipsum...',
                price=333,
                prepayment_percent=33,
                refund_percent=55,
                rooms_count=2,
                floors=2,
                beds=4,
                square=100,
                date_deleted=datetime.now()
            )
            # сохраняем их
            CategoriesGateway.save_category(category, session, file=file, file_name=file.name)
            CategoriesGateway.save_category(deleted_category, session, file=file, file_name=file.name)
            # проверяем, чтоб вернул только активные
            self.assertEqual(CategoriesGateway.get_all(session), [category])

    @patch('hotel_business_module.utils.file_manager.FileManager.save_file')
    def test_familiar(self, mock_save_file: Mock):
        """
        Тестирование получения списка похожих категорий
        """
        mock_save_file.return_value = 'C:\\images\\image1.jpg'
        file = Mock()
        cats_list = []
        tags_list = []
        with get_session() as session:
            # создаем категории
            for i in range(5):
                category = Category(
                    name=f'test_category{i}',
                    description='lorem ipsum...',
                    price=999,
                    prepayment_percent=10,
                    refund_percent=50,
                    rooms_count=2,
                    floors=1,
                    beds=2,
                    square=50
                )
                CategoriesGateway.save_category(category, session, file=file, file_name=file.name)
                cats_list.append(category)

            # создаем теги
            for i in range(2):
                tag = Tag(name=f'test_tag{i}')
                TagsGateway.save_tag(tag, session)
                tags_list.append(tag)

            cat1 = cats_list[0]
            cat2 = cats_list[1]
            cat3 = cats_list[2]
            # цепляем теги к категориям
            for tag in tags_list:
                CategoriesGateway.add_tag_to_category(cat1, tag, session)
                CategoriesGateway.add_tag_to_category(cat2, tag, session)
            CategoriesGateway.add_tag_to_category(cat3, tags_list[0], session)

            # проверяем чтоб вернуло только категории с общими тегами
            self.assertEqual(CategoriesGateway.get_familiar(cat1, session), [cat2, cat3])
